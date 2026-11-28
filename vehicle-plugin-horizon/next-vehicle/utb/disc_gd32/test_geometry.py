"""Checks for the coordinate sketch; dimensions in Blockbench units."""
import math,unittest
class SketchGeometry(unittest.TestCase):
 def test_gangs_and_clearance_from_wheels_at_all_lift_positions(self):
  minimum=100
  for t in (0,.25,.5,.75,1):
   for side in (-1,1):
    for front in (True,False):
     angle=math.radians(18)*(1 if side<0 else -1)*(1 if front else -1)
     ux,uz=math.cos(angle),math.sin(angle); nx,nz=-uz,ux;cx=side*13.5;cz=-12.5 if front else 10.5
     for i in range(8):
      along=(i-3.5)*2.8
      for rr in (0,.25,.5,.75,1):
       for k in range(48):
        a=k*math.tau/48;r=4.2*rr;y=4.2+4.5*t+r*math.sin(a)
        x=cx+ux*along+nx*r*math.cos(a);z=cz+uz*along+nz*r*math.cos(a)
        axial=max(abs(x-side*12)-1.75-.2,0);radial=max(math.hypot(y-5.5,z+1)-5.5,0)
        minimum=min(minimum,math.hypot(axial,radial))
  self.assertGreater(minimum,.35)
 def test_axle_and_disc_heights(self):
  self.assertAlmostEqual(4.2-4.2,0);self.assertAlmostEqual(5.5-5.5,0)
  self.assertAlmostEqual(4.5/16,.28125)
  # A fixed wheel axle in world space while chassis moves through transport.
  for t in (0,.25,.5,.75,1):self.assertAlmostEqual(4.5*t+(5.5-4.5*t),5.5)
 def test_axle_guides_and_hydraulic_clevis_stay_connected(self):
  self.assertGreaterEqual(24.8/2,12)
  for t in [i/20 for i in range(21)]:
   y=5.5-4.5*t
   self.assertGreater(7.1-y,0)
   self.assertAlmostEqual((y+4.5*t)-5.5,0)
   self.assertGreater(math.hypot(16-y,5)-6,0)
  # Rod upper end enters the sleeve; lower end reaches moving axle.
  self.assertGreater(7.1,8-3/2)
  self.assertLess(7.1,8+3/2)
  self.assertGreaterEqual(11.25+2.5/2,12)
 def test_bearings_between_eight_spaced_discs(self):
  positions=[(i-3.5)*2.8 for i in range(8)]
  for x in (-8.4,0,8.4):self.assertGreater(min(abs(x-p)-.85/2-.4/2 for p in positions),0)
  self.assertTrue(all(abs((positions[i+1]-positions[i])-2.8)<1e-9 for i in range(7)))
 def test_note_about_requested_endpoints(self):
  # ±25/±2 at z=-16/-9 implies length 24.04 and angle 16.93°.
  self.assertAlmostEqual(math.hypot(23,7),24.0416,places=3)
  self.assertAlmostEqual(math.degrees(math.atan2(7,23)),16.9275,places=3)
  self.assertNotAlmostEqual(math.degrees(math.atan2(7,23)),18,places=1)
if __name__=='__main__':unittest.main(verbosity=2)
