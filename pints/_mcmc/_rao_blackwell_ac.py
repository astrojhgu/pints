#
# Rao-Blackwell Adaptive MCMC method
#
# This file is part of PINTS.
#  Copyright (c) 2017-2019, University of Oxford.
#  For licensing information, see the LICENSE file distributed with the PINTS
#  software package.
#
from __future__ import absolute_import, division
from __future__ import print_function, unicode_literals
import pints
import numpy as np


class RaoBlackwellACMC(pints.GlobalAdaptiveCovarianceMC):
    """
    Rao-Blackwell adaptive MCMC, as described by Algorithm 3 in [1]_.
        After initialising mu0 and sigma0, in each iteration after initial
        phase (t), the following steps occur::

        theta* ~ N(theta_t, lambda * sigma0)
        alpha(theta_t, theta*) = min(1, p(theta*|data) / p(theta_t|data))
        u ~ uniform(0, 1)
        if alpha(theta_t, theta*) > u:
            theta_t+1 = theta*
        else:
            theta_t+1 = theta_t
        mu_t+1 = mu_t + gamma_t+1 * (theta_t+1 - mu_t)
        sigma_t+1 = sigma_t + gamma_t+1 *
                        (bar((theta_t+1 - mu_t)(theta_t+1 - mu_t)') - sigma_t)

    where::

        bar(theta_t+1) = alpha(theta_t, theta*) theta* +
                            (1 - alpha(theta_t, theta*)) theta_t

    Note that we deviate from the paper in two places::

        gamma_t = t^-eta
        Y_t+1 ~ N(theta_t, lambda * sigma0) rather than
            Y_t+1 ~ N(theta_t, sigma0)

    Extends :class:`GlobalAdaptiveCovarianceMC`.

    References
    ----------
    .. [1] A tutorial on adaptive MCMC
           Christophe Andrieu and Johannes Thoms, Statistical Computing, 2008,
           18: 343-373.
           https://doi.org/10.1007/s11222-008-9110-y
    """
    def __init__(self, x0, sigma0=None):
        super(RaoBlackwellACMC, self).__init__(x0, sigma0)

        # heuristic based on normal approximation
        self._lambda = (2.38**2) / self._n_parameters

        self._X = None
        self._Y = None

    def ask(self):
        """ See :meth:`SingleChainMCMC.ask()`. """
        super(RaoBlackwellACMC, self).ask()

        # Propose new point
        if self._proposed is None:
            self._proposed = np.random.multivariate_normal(
                self._current, self._lambda * self._sigma)

            # Set as read-only
            self._proposed.setflags(write=False)

        # Return proposed point
        return self._proposed

    def n_hyper_parameters(self):
        """ See :meth:`TunableMethod.n_hyper_parameters()`. """
        return 1

    def name(self):
        """ See :meth:`pints.MCMCSampler.name()`. """
        return 'Rao-Blackwell adaptive covariance MCMC'

    def tell(self, fx):
        """ See :meth:`pints.AdaptiveCovarianceMCMC.tell()`. """
        self._Y = np.copy(self._proposed)
        self._X = np.copy(self._current)

        super(RaoBlackwellACMC, self).tell(fx)

        return self._current

    def _update_sigma(self):
        """
        Updates sigma using Rao-Blackwellised formula::

            sigma_t+1 = sigma_t + gamma_t+1 *
                        (bar((theta_t+1 - mu_t)(theta_t+1 - mu_t)') - sigma_t)

        where::

            bar(X_t+1) = alpha(X_t, Y_t+1) * Y_t+1 +
                            (1 - alpha(X_t, Y_t+1)) * X_t
        """
        acceptance_prob = (
            np.minimum(1, np.exp(self._log_acceptance_ratio)))
        X_bar = acceptance_prob * self._Y + (1.0 - acceptance_prob) * self._X
        dsigm = np.reshape(X_bar - self._mu, (self._n_parameters, 1))
        self._sigma = ((1 - self._gamma) * self._sigma +
                       self._gamma * np.dot(dsigm, dsigm.T))
