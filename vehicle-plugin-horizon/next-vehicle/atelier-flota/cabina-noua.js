/* Concept separat, inspirat de proporțiile unei cabine Iveco Daily de tractare:
 * https://www.gmpcars.co.uk/detail/1366339/used-iveco-daily-35s14b-2-3-35s14b-recovery-truck-lwb-preston
 * Nu modifică modelul sau JAR-ul instalat. Fața este -Z, puntea începe la -.15.
 * Ferestrele sunt goluri intenționate, fără panouri albastre. */
export const cabinaNoua = [
 // Longer frame, bumper and front landing step, all tied to the existing deck.
 ['chassis',-.78,.48,-.95,.18,.22,4.45],['chassis',.78,.48,-.95,.18,.22,4.45],
 ['chassis',0,.48,-2.68,2.15,.18,.18],['chassis',0,.48,-.32,2.15,.18,.18],
 ['chassis',0,.46,-3.13,2.70,.24,.20],['steel',0,.51,-3.25,2.20,.08,.06],
 ['steel',-1.16,.45,-3.22,.32,.16,.12],['steel',1.16,.45,-3.22,.32,.16,.12],
 ['white',0,.50,-3.265,.48,.12,.02],['dark',0,.50,-3.28,.34,.03,.02],
 // Floor and low nose: no opaque wall behind the windscreen.
 ['chassis',0,.70,-1.62,2.26,.17,2.64],
 ['white',0,.91,-2.85,2.64,.42,.40],['white',0,1.14,-2.84,2.58,.08,.45],
 ['whiteDark',0,1.12,-2.58,2.52,.12,.12],
 // Nose joins the pillars; the wheel opening remains unobstructed below.
 ['white',0,1.16,-2.54,2.54,.20,.22],
 // Front: inset broad grille, separated lamp pockets, horizontal brightwork.
 ['dark',0,.91,-3.065,1.65,.35,.04],['black',0,.91,-3.091,1.51,.27,.018],
 ['steel',0,1.035,-3.105,1.54,.025,.015],['steel',0,.785,-3.105,1.54,.025,.015],
 ['silver',0,.975,-3.111,1.43,.022,.012],['steel',0,.910,-3.111,1.43,.020,.012],['silver',0,.845,-3.111,1.43,.022,.012],
 // Raised Horizon H emblem with a dark bezel rather than a flat block.
 ['black',0,.91,-3.126,.25,.19,.028],['silver',-.065,.91,-3.147,.035,.14,.018],
 ['silver',.065,.91,-3.147,.035,.14,.018],['silver',0,.91,-3.15,.13,.035,.018],
 // Four-element headlights with lower amber indicator strips.
 ['dark',-1.055,.94,-3.075,.49,.29,.045],['dark',1.055,.94,-3.075,.49,.29,.045],
 ['silver',-1.055,.94,-3.104,.45,.25,.020],['silver',1.055,.94,-3.104,.45,.25,.020],
 ['black',-1.055,.96,-3.119,.40,.19,.015],['black',1.055,.96,-3.119,.40,.19,.015],
 ['light',-1.145,.975,-3.130,.16,.12,.010],['light',-.965,.975,-3.130,.16,.12,.010],
 ['light',1.145,.975,-3.130,.16,.12,.010],['light',.965,.975,-3.130,.16,.12,.010],
 ['amber',-1.055,.865,-3.133,.39,.035,.012],['amber',1.055,.865,-3.133,.39,.035,.012],
 // Deep lower intake, fog lights, steel bumper and twin recovery points.
 ['black',0,.63,-3.139,1.34,.14,.025],['steel',0,.64,-3.156,1.19,.025,.012],
 ['dark',-1.08,.62,-3.145,.36,.14,.025],['dark',1.08,.62,-3.145,.36,.14,.025],
 ['light',-1.08,.63,-3.163,.26,.065,.012],['light',1.08,.63,-3.163,.26,.065,.012],
 ['steel',-.81,.46,-3.28,.22,.17,.07],['steel',.81,.46,-3.28,.22,.17,.07],
 ['dark',-.81,.46,-3.322,.10,.09,.018],['dark',.81,.46,-3.322,.10,.09,.018],
 // Shaped hood shoulders and a subtle pressed centre section.
 ['whiteDark',-.96,1.19,-2.83,.18,.035,.38],['whiteDark',.96,1.19,-2.83,.18,.035,.38],
 ['white',0,1.20,-2.86,1.40,.035,.34],
 // Continuous lower cab: doors sit BEHIND the front wheel openings.
 // The rear bulkhead closes the cabin below the rear window opening.
 ['white',-1.30,1.00,-.925,.12,.64,1.05],['white',1.30,1.00,-.925,.12,.64,1.05],
 ['white',0,1.02,-.40,2.48,.64,.12],
 ['whiteDark',-1.31,1.31,-1.40,.11,.08,1.98],['whiteDark',1.31,1.31,-1.40,.11,.08,1.98],
 ['white',-1.30,1.18,-1.99,.12,.20,1.18],['white',1.30,1.18,-1.99,.12,.20,1.18],
 // Door seams and handles attach directly to the door panels.
 ['dark',-1.369,.99,-.48,.018,.47,.025],['dark',1.369,.99,-.48,.018,.47,.025],
 ['dark',-1.369,.99,-1.42,.018,.47,.025],['dark',1.369,.99,-1.42,.018,.47,.025],
 ['dark',-1.369,1.08,-.93,.02,.05,.23],['dark',1.369,1.08,-.93,.02,.05,.23],
 ['silver',-1.383,1.09,-.93,.014,.022,.15],['silver',1.383,1.09,-.93,.014,.022,.15],
 ['dark',-1.369,.89,-.95,.018,.035,.86],['dark',1.369,.89,-.95,.018,.035,.86],
 // Four upright pillars meet both the continuous sill and the roof.
 ['white',-1.24,2.04,-2.39,.14,1.57,.16],['white',1.24,2.04,-2.39,.14,1.57,.16],
 ['white',-1.24,2.04,-.40,.14,1.57,.14],['white',1.24,2.04,-.40,.14,1.57,.14],
 ['white',0,2.87,-1.41,2.68,.16,2.20],
 ['whiteDark',0,2.76,-2.39,2.43,.08,.16],['white',0,2.73,-.40,2.41,.10,.14],
 ['white',0,1.36,-.40,2.41,.10,.14],['whiteDark',0,1.29,-2.39,2.42,.10,.15],
 // All four window apertures deliberately contain no blue glass or infill.
 // Visor, mirrors, amber markers and steps.
 ['whiteDark',0,2.80,-2.53,2.52,.08,.27],['white',0,2.86,-2.54,2.68,.07,.32],
 ['dark',0,2.77,-2.685,1.86,.025,.025],
 ['silver',-.97,2.77,-2.68,.11,.035,.03],['silver',.97,2.77,-2.68,.11,.035,.03],
 ['amber',-.88,2.98,-1.65,.27,.08,.28],['amber',.88,2.98,-1.65,.27,.08,.28],
 ['dark',-1.42,1.91,-2.39,.33,.07,.08],['dark',1.42,1.91,-2.39,.33,.07,.08],
 ['dark',-1.58,1.91,-2.39,.13,.43,.19],['dark',1.58,1.91,-2.39,.13,.43,.19],
 ['silver',-1.66,1.91,-2.39,.015,.33,.13],['silver',1.66,1.91,-2.39,.015,.33,.13],
 ['chassis',-1.20,.45,-.95,.22,.16,1.15],['chassis',1.20,.45,-.95,.22,.16,1.15],
 ['steel',-1.38,.45,-.95,.30,.10,1.15],['steel',1.38,.45,-.95,.30,.10,1.15],
 ['dark',-1.40,.52,-.95,.27,.025,1.06],['dark',1.40,.52,-.95,.27,.025,1.06],
 // Interior: independent seats, backrests, dash and center console.
 ['dashboard',0,1.36,-2.20,2.30,.22,.45],
 ['dark',-.61,1.49,-2.00,.58,.10,.16],['silver',-.61,1.55,-2.02,.32,.025,.045],
 ['seat',-.62,.98,-1.20,.72,.23,.71],['seat',.62,.98,-1.20,.72,.23,.71],
 ['seat',-.62,1.38,-.84,.72,.72,.16,-.08],['seat',.62,1.38,-.84,.72,.72,.16,-.08],
 ['seat',-.62,1.87,-.82,.36,.23,.14],['seat',.62,1.87,-.82,.36,.23,.14],
 ['chassis',0,1.03,-1.43,.26,.36,.85],['black',.12,1.31,-1.36,.05,.30,.05,-.25],
 ['black',.12,1.48,-1.40,.10,.10,.10],
 // Front axle and short arch caps, kept above/outside the wheel envelope.
 ['chassis',0,.53,-2.05,2.55,.12,.13],
 ['white',-1.31,1.13,-2.05,.15,.10,1.19],['white',1.31,1.13,-2.05,.15,.10,1.19],
 ['white',-1.31,.84,-2.65,.15,.40,.10],['white',1.31,.84,-2.65,.15,.40,.10],
 ['white',-1.31,.84,-1.44,.15,.40,.10],['white',1.31,.84,-1.44,.15,.40,.10],
];
export const frontWheels=[[-1.35,.53,-2.05,1.18],[1.35,.53,-2.05,1.18]];
export const steeringPosition=[-.62,1.52,-1.95];
