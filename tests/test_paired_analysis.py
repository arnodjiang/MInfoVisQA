import unittest
import numpy as np
from scripts.evaluation.paired_analysis import seed_metrics, estimate

class PairedAnalysisTests(unittest.TestCase):
    def test_language_invariant_correctness(self):
        y=np.array([[1]*24,[0]*24])
        m=seed_metrics(y,0)
        np.testing.assert_array_equal(m[:,2:],0)
        self.assertEqual((y.sum(1)>=24).mean(),.5)

    def test_flips_cancel_despite_zero_net_change(self):
        y=np.array([[1,0,1],[0,1,0]])
        m=seed_metrics(y,0).mean(0)
        self.assertEqual(m[2],0)
        self.assertEqual(m[3],25)
        self.assertEqual(m[4],25)

    def test_net_and_subgroup_identities(self):
        y=np.random.default_rng(19).integers(0,2,(128,24))
        for b in [0,1]:
            m=seed_metrics(y,b)
            np.testing.assert_allclose(m[:,2],m[:,4]-m[:,3],atol=1e-12)
            self.assertAlmostEqual(m[:,2].mean(),(87*m[:87,2].mean()+41*m[87:,2].mean())/128)

    def test_bootstrap_is_reproducible_and_clustered(self):
        m=seed_metrics(np.array([[1]*24,[0]*24]),0)
        a=estimate(m,1000,9)
        self.assertEqual(a,estimate(m,1000,9))
        self.assertEqual(a['n_seeds'],2)
        self.assertEqual(a['ci95'][2],[0,0])
        self.assertEqual(a['ci95'][0],[0,100])
        self.assertIsNone(estimate(np.empty((0,5)))['point'])

class PlotModelCoverageTests(unittest.TestCase):
    def test_more_than_four_models_are_not_dropped(self):
        from pathlib import Path
        from unittest.mock import patch
        import os
        os.environ.setdefault('MPLCONFIGDIR','/tmp/minfovisqa-mpl')
        from matplotlib.figure import Figure
        from scripts.evaluation.paired_analysis import plot
        rows=[{'model':f'Model {i}','query_language':q,'k':k,'coverage_pct':100-k}
              for i in range(9) for q in ['en','zh'] for k in range(1,25)]
        captured=[]
        with patch.object(Figure,'savefig',lambda fig,*a,**kw:captured.append(fig)):
            plot(Path('/tmp'),rows)
        self.assertEqual(len(captured[0].axes[0].lines),9)
        self.assertEqual(len(captured[0].axes[1].lines),9)
        self.assertEqual(len(captured[0].legends[0].texts),9)

if __name__=='__main__':unittest.main()
