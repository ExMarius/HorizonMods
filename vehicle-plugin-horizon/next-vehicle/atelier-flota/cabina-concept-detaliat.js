/* Concept only. Coordinates in blocks; front is -Z. No game files are changed. */
export const body=[], roof=[], interior=[];
const add=(group,mat,x,y,z,w,h,d,rx=0)=>group.push([mat,x,y,z,w,h,d,rx]);
const pair=(group,mat,x,y,z,w,h,d,rx=0)=>{for(const side of [-1,1])add(group,mat,x*side,y,z,w,h,d,rx)};
// Full-width nose, lower valance and bumper cover the gap under the front.
add(body,'chassis',0,.40,-2.61,2.66,.27,.23);
add(body,'dark',0,.58,-2.59,2.60,.12,.17);
// Solid lower front belly pan connects the bumper to the chassis and floor.
add(body,'chassis',0,.32,-2.30,2.12,.16,.50);
add(body,'dark',0,.48,-2.30,2.12,.16,.48);
add(body,'chassis',0,.56,-1.83,2.12,.16,.46);
add(body,'white',0,.85,-2.48,2.60,.47,.34);
add(body,'whiteDark',0,1.105,-2.43,2.55,.07,.40);
add(body,'white',0,1.155,-2.38,2.53,.04,.42);
pair(body,'dark',1.07,.66,-2.685,.34,.11,.035);
pair(body,'light',1.07,.66,-2.708,.23,.055,.012);
add(body,'black',0,.62,-2.69,1.18,.12,.025);
add(body,'steel',0,.62,-2.708,1.05,.025,.012);
pair(body,'dark',.88,.39,-2.75,.17,.12,.07);
pair(body,'silver',.88,.39,-2.795,.075,.055,.016);
// Main grille and recessed lamps, with separate surfaces instead of coplanar layers.
add(body,'dark',0,.87,-2.662,1.54,.31,.025);
for(const y of [.77,.84,.91,.98])add(body,'silver',0,y,-2.681,1.37,.014,.012);
add(body,'black',0,.89,-2.696,.22,.14,.015);
pair(body,'silver',.055,.89,-2.709,.025,.10,.008);
add(body,'silver',0,.89,-2.713,.09,.024,.008);
pair(body,'dark',1.03,.90,-2.666,.43,.29,.035);
pair(body,'light',1.03,.945,-2.689,.35,.13,.01);
pair(body,'amber',1.03,.835,-2.689,.35,.04,.01);
// Frame, flat floor, wheelhouse walls: the tyre stays outside the footwell.
pair(body,'chassis',.85,.44,-1.45,.16,.19,2.25);
add(body,'chassis',0,.69,-1.42,2.18,.16,2.20);
// Closed firewall and lower interior side trims connect floor to dashboard.
add(body,'dashboard',0,1.005,-2.225,2.18,.47,.06);
pair(body,'dashboard',1.17,1.04,-.69,.12,.54,.62);
pair(body,'dark',1.11,1.31,-.69,.025,.06,.62);
pair(body,'dashboard',1.10,.99,-1.66,.07,.48,1.10);
pair(body,'dashboard',1.01,1.245,-1.66,.20,.045,1.10);
// Wheel arch crown and front/rear arch edges; doors end behind the front tyre.
pair(body,'white',1.31,1.12,-1.66,.14,.12,1.18);
// Fill the former strip between arch crown and the window sill.
pair(body,'white',1.30,1.2525,-1.66,.13,.145,1.18);
pair(body,'white',1.31,.83,-2.28,.14,.45,.10);
pair(body,'white',1.31,.83,-1.04,.14,.45,.10);
pair(body,'white',1.30,1.01,-.66,.14,.63,.65);
pair(body,'whiteDark',1.30,1.36,-1.48,.13,.07,1.68);
// The rear end of the door and sill meet the rear corner, not open air.
pair(body,'white',1.30,1.01,-.345,.14,.63,.12);
// Close the lower step riser and the front and rear door jambs.
pair(body,'whiteDark',1.30,.61,-.67,.14,.17,.68);
pair(body,'white',1.30,1.01,-1.005,.14,.63,.05);
pair(body,'white',1.30,1.01,-.315,.14,.63,.06);
pair(body,'whiteDark',1.30,1.36,-.49,.13,.07,.30);
pair(body,'dark',1.378,1.08,-.65,.015,.045,.20);
pair(body,'silver',1.391,1.09,-.65,.012,.018,.13);
pair(body,'chassis',1.25,.44,-.67,.22,.16,.68);
pair(body,'whiteDark',1.30,.655,-.67,.14,.08,.68);
pair(body,'steel',1.39,.49,-.67,.18,.07,.68);
pair(body,'dark',1.39,.531,-.67,.16,.012,.59);
// Closed rear wall, narrow high rear window, and a shallow transition to bed.
add(body,'white',0,1.38,-.27,2.46,1.40,.14);
add(body,'white',0,2.06,-.27,2.46,.10,.14);
pair(body,'white',1.06,2.32,-.27,.34,.45,.14);
add(body,'whiteDark',0,2.56,-.27,2.47,.07,.14);
add(body,'chassis',0,.55,-.12,2.36,.18,.26);
pair(body,'dark',1.16,.50,-.10,.12,.28,.20);
// A-pillars, windscreen sill, mirror brackets; window apertures left empty.
pair(body,'white',1.24,1.98,-2.19,.14,1.35,.16);
pair(body,'white',1.24,2.00,-.27,.14,1.30,.14);
// Central window/door pillar connects the sill to the roof on each side.
pair(body,'white',1.24,2.00,-1.03,.14,1.30,.11);
pair(body,'dark',1.317,1.98,-1.03,.014,1.20,.035);
add(body,'whiteDark',0,1.30,-2.19,2.38,.12,.16);
// Continuous cowl closes the opening between hood and windscreen sill.
add(body,'white',0,1.225,-2.29,2.38,.10,.30);
pair(body,'dark',1.41,1.96,-2.18,.34,.06,.07);
pair(body,'dark',1.57,1.96,-2.18,.13,.38,.17);
pair(body,'silver',1.644,1.96,-2.18,.015,.28,.11);
// Roof can be hidden to inspect the passenger compartment.
add(roof,'white',0,2.68,-1.23,2.62,.14,2.10);
add(roof,'whiteDark',0,2.60,-2.19,2.40,.06,.16);
add(roof,'white',0,2.66,-2.28,2.56,.06,.24);
pair(roof,'amber',.83,2.79,-1.36,.23,.08,.23);
// Shaped dashboard, gauges, vents, switches, radio and glovebox.
add(interior,'dashboard',0,1.35,-1.98,2.20,.25,.38);
add(interior,'dark',-.62,1.50,-1.79,.59,.10,.13);
for(const x of [-.80,-.62,-.44]){
 add(interior,'black',x,1.558,-1.79,.13,.012,.10);
 add(interior,'silver',x,1.566,-1.78,.06,.008,.03);
}
for(const x of [-1.00,.80]){
 add(interior,'black',x,1.40,-1.781,.25,.12,.014);
 for(const y of [1.37,1.40,1.43])add(interior,'steel',x,y,-1.77,.20,.009,.008);
}
add(interior,'dark',.26,1.39,-1.78,.48,.18,.025);
add(interior,'black',.26,1.39,-1.758,.42,.13,.012);
add(interior,'silver',.19,1.41,-1.749,.20,.04,.008);
for(const x of [.35,.40,.45])add(interior,'silver',x,1.38,-1.748,.025,.025,.008);
add(interior,'dark',.78,1.25,-1.78,.56,.17,.025);
add(interior,'silver',.78,1.29,-1.761,.16,.02,.012);
// Console, shifter boot, stalk and knob; handbrake beside driver's cushion.
add(interior,'chassis',0,.98,-1.16,.28,.40,.82);
add(interior,'dark',.04,1.20,-1.18,.18,.08,.18);
add(interior,'steel',.04,1.31,-1.18,.055,.17,.055,-.15);
add(interior,'black',.04,1.42,-1.20,.10,.09,.10);
add(interior,'dark',-.21,1.11,-.70,.11,.12,.25);
add(interior,'black',-.21,1.22,-.70,.045,.18,.045,-.30);
add(interior,'black',-.21,1.32,-.73,.075,.06,.12);
// Cushions, bolsters, backrest and headrest scaled to a Minecraft player.
for(const x of [-.62,.62]){
 add(interior,'chassis',x,.85,-.80,.48,.16,.49);
 add(interior,'seat',x,.99,-.80,.58,.15,.58);
 for(const side of [-1,1])add(interior,'dark',x+side*.27,1.06,-.80,.07,.11,.56);
 add(interior,'seat',x,1.39,-.48,.58,.68,.13);
 for(const side of [-1,1])add(interior,'dark',x+side*.27,1.40,-.48,.07,.62,.15);
 add(interior,'seat',x,1.82,-.48,.36,.19,.15);
 add(interior,'black',x,.782,-1.22,.64,.014,.45);
}
// Foot controls: three distinct pedals, with rubber grip strips.
for(const x of [-.90,-.65,-.40]){
 add(interior,'steel',x,.93,-1.76,.035,.25,.045,-.15);
 add(interior,'dark',x,1.05,-1.73,.15,.09,.075);
 for(const dx of [-.045,0,.045])add(interior,'silver',x+dx,1.051,-1.687,.009,.05,.008);
}
export const frontWheels=[[-1.35,.53,-1.66,1.18],[1.35,.53,-1.66,1.18]];
export const steeringPosition=[-.62,1.48,-1.68];
// Clearance behind the dashboard; moves the rim toward the fixed driver seat.


// Toolbox mounted directly below the deck with visible brackets and a rear face.
export const underbed=[];
add(underbed,'chassis',-1.02,.49,2.08,.44,.40,.88);
add(underbed,'steel',-1.247,.49,2.08,.025,.35,.82);
add(underbed,'dark',-1.264,.49,2.08,.012,.27,.73);
add(underbed,'steel',-1.273,.49,2.08,.008,.22,.68);
add(underbed,'black',-1.280,.52,2.08,.008,.04,.13);
for(const z of [1.73,2.43]){
 add(underbed,'chassis',-1.00,.71,z,.38,.09,.09);
 add(underbed,'steel',-1.24,.695,z,.06,.11,.09);
}

// Shorten only ahead of the fixed seat reference; width and seat geometry stay unchanged.
const seatZ=-.80, frontCompression=.80;
export function compactCabZ(z){return z < seatZ ? seatZ+(z-seatZ)*frontCompression : z;}
export const steeringZ=compactCabZ(-1.68)+.13;
export function compactCabPiece(part, group){
 const [kind,x,y,z,w,h,d]=part;
 // Keep both seats, their bases, bolsters and headrests exactly where they were.
 if(group==='interior' && z>=-1.10) return [...part];
 const near=compactCabZ(z+d/2), far=compactCabZ(z-d/2);
 const result=[...part];result[3]=(near+far)/2;result[6]=near-far;
 // Full-size tyres still need their original clear opening after shortening.
 const axle=compactCabZ(-1.66);
 if(group==='body' && Math.abs(x)===1.31 && kind==='white'){
  if(y===1.12 && z===-1.66){result[3]=axle;result[6]=1.18;}
  if(y===.83 && z===-2.28){result[3]=axle-.62;result[6]=.10;}
  if(y===.83 && z===-1.04){result[3]=axle+.62;result[6]=.10;}
 }
 return result;
}
