import unittest,json,tomllib
from pathlib import Path
import numpy as np
from logos_recovery import __version__,models
from logos_recovery.synthetic import generate,evaluate

ROOT=Path(__file__).resolve().parents[1]

class ScienceChecks(unittest.TestCase):
    def test_frozen_candidates_and_independent_solver(self):
        refs=json.loads((ROOT/'data/candidate_benchmarks.json').read_text())['candidates']
        for ref in refs:
            with self.subTest(run=ref['run_id']):
                got,trace=models.periodic(ref['T'],ref['f'])
                ind,_=models.periodic(ref['T'],ref['f'],method='Radau',rtol=2e-12)
                for key in ['J','peak_Z']:
                    self.assertLess(abs(got[key]-ref[key]),1e-8)
                    self.assertLess(abs(got[key]-ind[key]),1e-8)
                self.assertLess(got['closure_residual'],1e-8)
                self.assertAlmostEqual(got['mean_C'],1.,places=13)
                self.assertTrue(((trace.R>=0)&(trace.R<=1)).all())
                self.assertTrue((trace.Z>=0).all())
                for key,val in ref['initial_periodic_state'].items():
                    self.assertLess(abs(trace[key].iloc[0]-val),1e-8)

    def test_constant_reference_and_null(self):
        j,z=models.reference()
        expected_R = 1/(2+(1/.35)**4)
        self.assertAlmostEqual(j,.5*expected_R-.04,places=13)
        self.assertAlmostEqual(z,2/7,places=12)
        p=dict(models.P,control='R_clamped')
        periods=np.array([.2,1.679033,8.,30.]);j,_=models.screen(periods,np.array([.2,.2,.5,.95]),p,N=1024)
        self.assertTrue(np.all(j<=models.reference(p)[0]+1e-7))

    def test_finite_budget_tail_and_mass_balance(self):
        results,_=models.finite()
        expected={'Constant':(-.021674451,.285435225),'Cycle':(.0552361206,.188359664)}
        for _,row in results.iterrows():
            self.assertEqual(row.administered_amount,20)
            self.assertLess(row.mass_balance_error,1e-9)
            self.assertLess(abs(row.J_F-expected[row.regimen][0]),1e-8)
            self.assertLess(abs(row.peak_Z-expected[row.regimen][1]),1e-8)
            self.assertLess(row.remaining_exposure,1e-8)

    def test_palbociclib_matched_amounts(self):
        results,_=models.palbociclib()
        self.assertTrue((results.administered_mg==15750).all())
        np.testing.assert_allclose(results.nadir_ANC,[1.126817,1.346779],atol=1e-6,rtol=0)

    def test_synthetic_provenance_and_reproducibility(self):
        a=generate();b=generate()
        self.assertTrue(a.equals(b));self.assertEqual(len(a),144)
        self.assertTrue(a.is_synthetic.all());self.assertTrue(a.subject.str.startswith('SYN-').all())
        saved=ROOT/'data/synthetic_restart_panel.csv'
        import pandas as pd
        np.testing.assert_allclose(pd.read_csv(saved).minimum_ANC,a.minimum_ANC,atol=1e-11)
        result=evaluate(a);self.assertTrue(np.isfinite(result[['rmse_calendar','rmse_state']]).all().all())

    def test_version(self):
        with (ROOT/'pyproject.toml').open('rb') as f:p=tomllib.load(f)['project']
        self.assertEqual(__version__,p['version'])
        self.assertEqual(p['requires-python'],'>=3.12,<3.13')
        self.assertIn('v'+__version__,(ROOT/'CHANGELOG.md').read_text())


class RestartChecks(unittest.TestCase):
    def test_interior_optimum_and_constraints(self):
        from logos_recovery.restart import constrained_wait,utility
        best=constrained_wait()
        self.assertAlmostEqual(best['wait'],np.log(.8/.06)/1.4,places=8)
        self.assertGreater(best['value'],utility(0))
        forced=constrained_wait(Z0=np.exp(5),Zsafe=1,p=1)
        self.assertTrue(forced['feasible']);self.assertFalse(forced['positive_value'])
        self.assertFalse(constrained_wait(Z0=np.exp(8))['feasible'])
        self.assertFalse(constrained_wait(D0=2,Dmax=1)['feasible'])
        self.assertEqual(constrained_wait(g=0)['wait'],6)
        self.assertEqual(constrained_wait(R0=1)['wait'],0)

if __name__=='__main__':unittest.main()
