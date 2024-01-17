#!/usr/bin/env python3

import pytest
import os
import numpy as np
import scipy.signal
import oct2py

print(oct2py.__version__)

CI = bool(os.environ.get("CI"))


def demo_fir():
    m = 7
    p = 0.2

    with oct2py.Oct2Py() as oc:
        oc.eval("pkg load signal")
        bmat = oc.fir1(m, p).squeeze()
    # %% Python
    bpy = scipy.signal.firwin(m + 1, p)
    # %% plot
    wmat, hmat = scipy.signal.freqz(bmat)
    wpy, hpy = scipy.signal.freqz(bpy)

    hmat_db = 20 * np.log10(abs(hmat))
    hpy_db = 20 * np.log10(abs(hpy))

    assert (hmat_db[:130] > -6).all()
    assert (hpy_db[:130] > -6).all()

    assert (hmat_db[278:] < -20).all()
    assert (hpy_db[278:] < -20).all()

    # disabled for old Octave 3.6
    # np.testing.assert_allclose(hpy_db, hmat_db, atol=5) # dB

    return wmat, hmat, wpy, hpy, hmat_db, hpy_db


def test_savgol():
    k = 3  # filter length
    n = 5  # filter order
    # %% noisy signal
    x = np.array([0.0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0])
    x += np.random.randn(x.size)
    # %% Octave
    with oct2py.Oct2Py(oned_as="column") as oc:
        oc.eval("pkg load signal")
        ymat = oc.sgolayfilt(x, k, n).squeeze()
    # %% Python
    ypy = scipy.signal.savgol_filter(x, n, k)
    # %% plot
    np.testing.assert_allclose(ypy, ymat)


@pytest.mark.skipif(CI, reason="CI's are not for viewing plots generally")
def test_plot_filter():
    from matplotlib.pyplot import figure, show

    wmat, hmat, wpy, hpy, hmat_db, hpy_db = demo_fir()

    figure(1).clf()
    ax = figure(1).subplots(2, 1, sharex=True)
    ax[0].set_title("FIR1() vs. firwin() frequency response")
    ax[0].plot(wmat, hmat_db, label="Matlab")
    ax[0].plot(wpy, hpy_db, label="Python")
    ax[0].set_ylabel("Amplitude [dB]")
    ax[0].grid(True)
    ax[0].legend()

    angmat = np.unwrap(np.angle(hmat))
    angpy = np.unwrap(np.angle(hpy))
    ax[1].plot(wmat, angmat, label="Matlab")
    ax[1].plot(wpy, angpy, label="Python")
    ax[1].set_ylabel("Angle (radians)")
    ax[1].grid(True)
    ax[1].set_xlabel("Frequency [rad/sample]")
    ax[1].legend()

    show()
