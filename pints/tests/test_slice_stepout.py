#!/usr/bin/env python3
#
# Tests the basic methods of the Slice Sampling routine.
#
# This file is part of PINTS.
#  Copyright (c) 2017-2019, University of Oxford.
#  For licensing information, see the LICENSE file distributed with the PINTS
#  software package.
#

import unittest
import numpy as np

import pints
import pints.toy as toy

from shared import StreamCapture

debug = False


class TestSliceStepout(unittest.TestCase):
    """
    Tests the basic methods of the Slice Sampling with Stepout routine.

    Please refer to the _slice_stepout.py script in ..\_mcmc\_slice_stepout.py
    """    
    def test_initialisation(self):
        """
        Tests whether all instance attributes are initialised correctly.
        """
        # Create mcmc
        x0 = np.array([2, 4])
        mcmc = pints.SliceStepoutMCMC(x0)

        # Test attributes initialisation
        self.assertFalse(mcmc._running)
        self.assertFalse(mcmc._ready_for_tell)
        self.assertFalse(mcmc._first_expansion)
        self.assertFalse(mcmc._interval_found)
        self.assertFalse(mcmc._set_l)
        self.assertFalse(mcmc._set_r)
        self.assertFalse(mcmc._init_left)
        self.assertFalse(mcmc._init_right)

        self.assertEqual(mcmc._current, None)
        self.assertEqual(mcmc._current_log_pdf, None)
        self.assertEqual(mcmc._current_log_y, None)
        self.assertEqual(mcmc._proposed, None)
        self.assertEqual(mcmc._l, None)
        self.assertEqual(mcmc._r, None)
        self.assertEqual(mcmc._temp_l, None)
        self.assertEqual(mcmc._temp_r, None)
        self.assertEqual(mcmc._k, None)
        self.assertEqual(mcmc._j, None)
        self.assertEqual(mcmc._fx_l, None)
        self.assertEqual(mcmc._fx_r, None)

        self.assertEqual(mcmc._m, 50)
        self.assertEqual(mcmc._mcmc_iteration, 0)
        self.assertEqual(mcmc._i, 0)



    def test_first_run(self):
        """
        Tests the very first run of the sampler. 
        """
        # Create log pdf
        log_pdf = pints.toy.GaussianLogPDF([2, 4], [[1, 0], [0, 3]])

        # Create mcmc
        x0 = np.array([2., 4.])
        mcmc = pints.SliceStepoutMCMC(x0)

        # Ask should fail if _ready_for_tell flag is True
        with self.assertRaises(RuntimeError):
            mcmc._ready_for_tell = True
            mcmc.ask()

        # Undo changes
        mcmc._ready_for_tell = False

        # Check whether _running flag becomes True when ask() is called
        # Check whether first iteration of ask() returns x0
        self.assertFalse(mcmc._running)
        self.assertTrue(np.all(mcmc.ask() == x0))
        self.assertTrue(mcmc._running)
        self.assertTrue(mcmc._ready_for_tell)

        # Tell should fail when log pdf of x0 is infinite
        with self.assertRaises(ValueError):
            fx = np.inf
            mcmc.tell(fx)

        # Calculate log pdf for x0
        fx = log_pdf.evaluateS1(x0)[0]

        # Tell should fail when _ready_for_tell is False
        with self.assertRaises(RuntimeError):
            mcmc._ready_for_tell = False
            mcmc.tell(fx)

        # Undo changes
        mcmc._ready_for_tell = True

        # Test first iteration of tell(). The first point in the chain should be x0
        self.assertTrue(np.all(mcmc.tell(fx) == x0))

        # We update the current sample
        self.assertTrue(np.all(mcmc._current == x0))
        self.assertTrue(np.all(mcmc._current == mcmc._proposed))

        # We update the _current_log_pdf value used to generate the new slice
        self.assertEqual(mcmc._current_log_pdf, fx)

        # Check that the new slice has been constructed appropriately 
        self.assertTrue(mcmc._current_log_y == (mcmc._current_log_pdf - mcmc._e))
        self.assertTrue(mcmc._current_log_y < mcmc._current_log_pdf)

        # Check flag
        self.assertTrue(mcmc._first_expansion)


    
    def test_cycle(self):
        """
        Tests every step of a single MCMC iteration.
        """
        # Set seed for monitoring
        np.random.seed(2)

        # Create log pdf
        log_pdf = pints.toy.GaussianLogPDF([2, 4], [[1, 0], [0, 3]])

        # Create mcmc
        x0 = np.array([2., 4.])
        mcmc = pints.SliceStepoutMCMC(x0)

        mcmc.set_w(1)
        # VERY FIRST RUN
        x = mcmc.ask()
        fx = log_pdf.evaluateS1(x)[0]
        sample = mcmc.tell(fx)
        self.assertTrue(np.all(sample == x0))
        self.assertEqual(mcmc._fx_l, None)
        self.assertEqual(mcmc._fx_r, None)

        ##################################
        ### FIRST PARAMETER  - INDEX 0 ###
        ##################################
        
        # FIRST 2 RUNS: create initial interval edges

        # Start with initiating edges and ask for log_pdf of left edge
        self.assertTrue(mcmc._first_expansion)
        x = mcmc.ask()
        self.assertFalse(mcmc._first_expansion)

        # Check that interval edges are initialised appropriately
        self.assertTrue(mcmc._l < mcmc._current[0])
        self.assertTrue(mcmc._r > mcmc._current[0])

        # Check that limits for interval expansion steps have been initialised 
        # appropriately
        self.assertTrue(mcmc._j <= 49)
        self.assertEqual(mcmc._k, (49 - mcmc._j))

        # We calculate the log pdf of the initial left interval edge
        fx = log_pdf.evaluateS1(x)[0]
        sample = mcmc.tell(fx)

        # Check that we have set the log_pdf of the initialised left edge correctly
        self.assertEqual(fx, mcmc._fx_l)

        # Ask for log_pdf of right edge
        self.assertFalse(mcmc._first_expansion)
        x = mcmc.ask()
        
        # We calculate the log pdf of the initial right interval edge
        fx = log_pdf.evaluateS1(x)[0]
        sample = mcmc.tell(fx)

        # Check that we have set the log_pdf of the initialised right edge correctly
        self.assertEqual(fx, mcmc._fx_r)
        
        # Check that flags for pdf of initial edges are False
        self.assertFalse(mcmc._init_left)
        self.assertFalse(mcmc._init_right)

        # THIRD RUN: begin expanding the interval
        x = mcmc.ask()

        # Check that the flag for updating the left edge has been set
        self.assertTrue(mcmc._set_l)
        
        # The left edge is still within the slice, co continue expanding to the left
        fx = log_pdf.evaluateS1(x)[0]
        sample = mcmc.tell(fx)
        self.assertEqual(sample, None)
        self.assertEqual(fx, mcmc._fx_l)

        # FOURTH RUN: Continue expanding the interval
        x = mcmc.ask()
        
        # Check that the flag for updating the left edge has been set
        self.assertTrue(mcmc._set_l)

        # The edges are not inside the slice: we have concluded the interval expansion 
        # to the left. Return None and update the log pdf of the left edge
        fx = log_pdf.evaluateS1(x)[0]
        sample = mcmc.tell(fx)
        self.assertEqual(sample, None)
        self.assertEqual(fx, mcmc._fx_l)
        
        # FIFTH RUN: Continue expanding the interval
        x = mcmc.ask()
        
        # Check that the flag for updating the left edge has been reset
        self.assertFalse(mcmc._set_l)

        # Check that the flag for updating the right edge has been reset
        self.assertTrue(mcmc._set_r)

        # The edges are not inside the slice: we have concluded the interval expansion 
        # to the right. Return None and update the log pdf of the left edge
        fx = log_pdf.evaluateS1(x)[0]
        sample = mcmc.tell(fx)
        self.assertEqual(sample, None)
        self.assertEqual(fx, mcmc._fx_r)

        # SIXTH RUN: We have expanded the interval. We now propose a trial point
        # uniformly distributed from the estimated interval
        x = mcmc.ask()

        # Check that the flags are set correctly
        self.assertFalse(mcmc._set_r)
        self.assertTrue(mcmc._interval_found)

        # The proposed point is in the slice, so it passes the ``Threshold Check``.
        fx = log_pdf.evaluateS1(x)[0]
        sample = mcmc.tell(fx)
        
        # Since we have accepted the value for the new parameter, we increase the index
        self.assertEqual(mcmc._i, 1)

        # We are moving to a new parameter, so we reset the flags for expanding
        # the interval of the new parameter
        self.assertTrue(mcmc._first_expansion)
        self.assertFalse(mcmc._interval_found)

        
        ###################################
        ### SECOND PARAMETER  - INDEX 1 ###
        ###################################

        # FIRST 2 RUNS: create initial interval edges
        self.assertTrue(mcmc._first_expansion)
        x = mcmc.ask()
        self.assertFalse(mcmc._first_expansion)

        # Check that interval edges are initialised appropriately
        self.assertTrue(mcmc._l < mcmc._current[1])
        self.assertTrue(mcmc._r > mcmc._current[1])

        # Check that limits for interval expansion steps have been initialised 
        # appropriately
        self.assertTrue(mcmc._j <= 49)
        self.assertEqual(mcmc._k, (49 - mcmc._j))

        # We calculate the log pdf of the initial left interval edge
        fx = log_pdf.evaluateS1(x)[0]
        sample = mcmc.tell(fx)

        # Check that we have set the log_pdf of the initialised left edge correctly
        self.assertEqual(fx, mcmc._fx_l)

        # Ask for log_pdf of right edge
        self.assertFalse(mcmc._first_expansion)
        x = mcmc.ask()
        
        # We calculate the log pdf of the initial right interval edge
        fx = log_pdf.evaluateS1(x)[0]
        sample = mcmc.tell(fx)

        # Check that we have set the log_pdf of the initialised right edge correctly
        self.assertEqual(fx, mcmc._fx_r)
        
        # Check that flags for pdf of initial edges are False
        self.assertFalse(mcmc._init_left)
        self.assertFalse(mcmc._init_right)

        
        # THIRD RUN: begin expanding the interval
        x = mcmc.ask()

        # Check that the flag for updating the left edge has been set
        self.assertTrue(mcmc._set_l)

        # The left edge is still within the slice, so continue expanding to the left
        fx = log_pdf.evaluateS1(x)[0]
        sample = mcmc.tell(fx)
        self.assertEqual(sample, None)
        self.assertEqual(fx, mcmc._fx_l)
        
        # FOURTH RUN: Continue expanding the interval
        x = mcmc.ask()
        
        # Check that the flag for updating the left edge has been set
        self.assertTrue(mcmc._set_l)

        # The edges are not inside the slice: we have concluded the interval expansion 
        # to the left. Return None and update the log pdf of the left edge
        fx = log_pdf.evaluateS1(x)[0]
        sample = mcmc.tell(fx)
        self.assertEqual(sample, None)
        self.assertEqual(fx, mcmc._fx_l)

        # FIFTH RUN: Continue expanding the interval
        x = mcmc.ask()

        # Check that the flag for updating the left edge has been reset
        self.assertFalse(mcmc._set_l)

        # Check that the flag for updating the right edge has been reset
        self.assertTrue(mcmc._set_r)

        # The right edge is still within the slice, co continue expanding to the right
        fx = log_pdf.evaluateS1(x)[0]
        sample = mcmc.tell(fx)
        self.assertEqual(sample, None)
        self.assertEqual(fx, mcmc._fx_r)

        # SIXTH RUN: Continue expanding the interval
        x = mcmc.ask()

        # Check that the flag for updating the left edge has been reset
        self.assertFalse(mcmc._set_l)

        # Check that the flag for updating the right edge has been reset
        self.assertTrue(mcmc._set_r)

        # The edges are not inside the slice: we have concluded the interval expansion 
        # to the right. Return None and update the log pdf of the left edge
        fx = log_pdf.evaluateS1(x)[0]
        sample = mcmc.tell(fx)
        self.assertEqual(sample, None)
        self.assertEqual(fx, mcmc._fx_r)

        # SEVENTH RUN: We have expanded the interval. We now propose a trial point
        # uniformly distributed from the estimated interval
        x = mcmc.ask()

        # Check that the flags are set correctly
        self.assertFalse(mcmc._set_r)
        self.assertTrue(mcmc._interval_found)

        # The proposed point is in the slice, so it passes the ``Threshold Check``.
        fx = log_pdf.evaluateS1(x)[0]
        sample = mcmc.tell(fx)

        # We have updated all the parameters for the new sample, so we move to the 
        # next sample and reset the index to 0
        self.assertEqual(mcmc._i, 0)

        # We are moving to a new parameter, so we reset the flags for expanding
        # the interval of the new parameter
        self.assertTrue(mcmc._first_expansion)
        self.assertFalse(mcmc._interval_found)

    
    def test_run(self):
        """
        Test multiple MCMC iterations of the sampler on a Multivariate Gaussian.
        """
        # Set seed for monitoring
        np.random.seed(2)

        # Create log pdf
        log_pdf = pints.toy.GaussianLogPDF([2, 4], [[1, 0], [0, 3]])

        # Create mcmc
        x0 = np.array([1,1])
        mcmc = pints.SliceStepoutMCMC(x0)

        # Run multiple iterations of the sampler
        chain = []
        while mcmc._mcmc_iteration < 10000:
            x = mcmc.ask()
            fx = log_pdf.evaluateS1(x)[0]
            sample = mcmc.tell(fx)
            if sample is not None:
                chain.append(np.copy(sample))

        # Fit Multivariate Gaussian to chain samples
        mean = np.mean(chain, axis=0)
        cov = np.cov(chain, rowvar=0)
        #print(mean) [2.00 4.00]
        #print(cov)  [[1.00, 0.01][0.01, 2.98]]


    def test_basic(self):
        """
        Test basic methods of the class.
        """
        # Create mcmc
        x0 = np.array([1,1])
        mcmc = pints.SliceStepoutMCMC(x0)

        # Test name
        self.assertEqual(mcmc.name(), 'Slice Sampling - Stepout')

        # Test set_w
        mcmc.set_w(2)
        self.assertTrue(np.all(mcmc._w == np.array([2,2])))
        with self.assertRaises(ValueError):
            mcmc.set_w(-1)

        # Test set_m
        mcmc.set_m(3)
        self.assertEqual(mcmc._m, 3.)
        with self.assertRaises(ValueError):
            mcmc.set_m(-1)

        # Test get_w
        self.assertTrue(np.all(mcmc.get_w() == np.array([2,2])))

        # Test get_m
        self.assertEqual(mcmc.get_m(), 3.)

        # Test current_log_pdf
        self.assertEqual(mcmc.current_log_pdf(), mcmc._current_log_pdf)

        # Test current_slice height
        self.assertEqual(mcmc.current_slice_height(), mcmc._current_log_y)

        # Test number of hyperparameters
        self.assertEqual(mcmc.n_hyper_parameters(), 2)

        # Test setting hyperparameters
        mcmc.set_hyper_parameters([3, 100])
        self.assertTrue((np.all(mcmc._w == np.array([3,3]))))
        self.assertEqual(mcmc._m, 100)

    
    def test_logistic(self):
        """
        Test sampler on a logistic task.
        """
        # Load a forward model
        model = toy.LogisticModel()

        # Create some toy data
        real_parameters = [0.015, 500]
        times = np.linspace(0, 1000, 1000)
        org_values = model.simulate(real_parameters, times)

        # Add noise
        noise = 10
        values = org_values + np.random.normal(0, noise, org_values.shape)
        real_parameters = np.array(real_parameters + [noise])

        # Get properties of the noise sample
        noise_sample_mean = np.mean(values - org_values)
        noise_sample_std = np.std(values - org_values)

        # Create an object with links to the model and time series
        problem = pints.SingleOutputProblem(model, times, values)

        # Create a log-likelihood function (adds an extra parameter!)
        log_likelihood = pints.GaussianLogLikelihood(problem)

        # Create a uniform prior over both the parameters and the new noise variable
        log_prior = pints.UniformLogPrior(
            [0.01, 400, noise * 0.1],
            [0.02, 600, noise * 100],
        )

        # Create a posterior log-likelihood (log(likelihood * prior))
        log_posterior = pints.LogPosterior(log_likelihood, log_prior)

        # Choose starting points for 3 mcmc chains
        num_chains = 1
        xs = [real_parameters * (1 + 0.1 * np.random.rand())]

        # Create mcmc routine
        mcmc = pints.MCMCController(
            log_posterior, num_chains, xs, method=pints.SliceStepoutMCMC)

        for sampler in mcmc.samplers():
            sampler.set_w(0.1)

        # Add stopping criterion
        mcmc.set_max_iterations(1000)

        # Set up modest logging
        mcmc.set_log_to_screen(True)
        mcmc.set_log_interval(500)

        # Run!
        print('Running...')
        chains = mcmc.run()
        print('Done!')



if __name__ == '__main__':
    print('Add -v for more debug output')
    import sys
    if '-v' in sys.argv:
        debug = True
    unittest.main()
    