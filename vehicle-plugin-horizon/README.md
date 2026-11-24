# Horizon integration working copy

This directory is a separate working copy of the selected November 5 baseline.
It is not automatically deployed. The initial integration provides the exact
group descriptor from the Horizon transfer and pivot/scale transformation
math with tests. It does not register or spawn the Horizon vehicle yet.
Keep `vehicle-plugin-nov5` unchanged as the verified rollback source.

A first separate `horizon_off_roader` integration now exists, with grouped
body, wheels, steering wheel and spare, and one driver seat. Its Paper physics
and passenger attachment are provisional: they are not claimed as source- or
visual-verified. Body paint uses the Horizon renderer’s full-body tint; off-road
wheels currently use the standard Horizon wheel visual. No automatic deploy.
