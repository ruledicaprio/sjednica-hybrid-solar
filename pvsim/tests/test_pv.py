import numpy as np
import pytest

from pvsim import config, pv


@pytest.fixture(scope="module")
def issu():
    return pv.ISSU(config.load("sjednica")["pv"]["issu"])


def test_issu_is_the_datasheet_at_every_point(issu):
    assert np.allclose(issu.efficiency(issu.pout_pts), issu.eta_pts, atol=1e-9)
    assert float(issu.efficiency(30.4 * 53.5)) == pytest.approx(0.9718, abs=1e-4)


def test_issu_holds_the_fixed_loss_below_the_curve(issu):
    assert issu.fixed_loss_w == pytest.approx(44.2, abs=0.3)
    assert float(issu.loss(100.0)) == pytest.approx(issu.fixed_loss_w)


def test_issu_output_inverts_the_loss_model(issu):
    p_in = np.array([300.0, 1500.0, 3000.0])
    out, clipped = issu.output(p_in, np.full(3, 25.0))
    assert np.allclose(out + issu.loss(out), p_in, atol=0.5)
    assert (clipped == 0).all()


def test_issu_clips_at_4kw_and_derates_when_hot(issu):
    out, clipped = issu.output(np.array([5000.0]), np.array([25.0]))
    assert out[0] == pytest.approx(4000.0) and clipped[0] > 0
    out, _ = issu.output(np.array([5000.0]), np.array([65.0]))
    assert out[0] == pytest.approx(3200.0)


def test_issu_gives_nothing_below_its_fixed_loss(issu):
    out, _ = issu.output(np.array([0.0, issu.fixed_loss_w * 0.5]),
                         np.array([20.0, 20.0]))
    assert (out == 0).all()


def test_huld_is_zero_in_the_dark():
    assert pv.huld_dc(np.array([0.0, 800.0]), np.array([10.0, 35.0]), 7020.0,
                      "pvgis5")[0] == 0.0


def test_tilt_table_interpolates():
    t = {"45": [0.08] * 12, "60": [0.04] * 12}
    assert pv.tilt_table(t, 52.5)[0] == pytest.approx(0.06)
    assert pv.tilt_table(t, 30)[0] == pytest.approx(0.08)
