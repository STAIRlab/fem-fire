wipe all;
model BasicBuilder -ndm 3 -ndf 6;
# set dataDir OUTPUT;
set script_path [file dirname [info script]]
cd $script_path

set dataDir E_fy_output
file mkdir $dataDir;

#NODAL DEFINITIONS
node 1 0 0 0;
node 2 1000 0 0;

#BOUNDRY CONDITIONS
fix 1 1 1 1 1 1 1;  

#Steel01Thermal Material properties
set Es 210000; 		#MPa	# steel initial Young's modulus;
set Fy 250;			#MPa	# steel initial yield strength;
set b 0.001;		#0.1%	# strain-hardening  ratio;

set matTag 1;
uniaxialMaterial Steel01Thermal $matTag $Fy $Es $b;

set secTag 1;

section FiberThermal $secTag -GJ $Es {
    patch quad $matTag 15 15 -50 -50 50 -50 50 50 -50 50}

set beamTransfTag 1;
geomTransf Linear $beamTransfTag 0 0 1;# y z x

element dispBeamColumnThermal 1 1 2 5 $secTag $beamTransfTag;

set gravity_force1 -1; # Not consider the weight of the floor slab
pattern Plain 1 Linear {
    eleLoad -ele 1 -type -beamUniform 0 $gravity_force1 0 ;
}

set pull_force 100;
pattern Plain 2 Linear {
    load 2 $pull_force 0 0 0 0 0;
}

set Tol 1.0e-8;            # convergence tolerance for test
set NstepGravity 10;       # apply gravity in 10 steps

constraints Plain;
numberer RCM;
system UmfPack;
test NormDispIncr $Tol $NstepGravity 500;
algorithm Newton;
integrator LoadControl [expr 1.0/$NstepGravity];
analysis Static;
analyze $NstepGravity;

puts "Gravity Loading done"

loadConst -time 0.0


recorder Element -file $dataDir/FiberStressStrain.out -time -ele 1 section 3 fiber 0 0 stressStrain;
# recorder Node -file $dataDir/NodesDisp.out -time -node 1 2 3 4 5 -dof 1 2 3 disp;

# fire analysis
puts "Fire Loading"

set Y1 -50;
set Y2 50;
set T_end 600;

pattern Plain 11 Linear {
    eleLoad -ele 1 -type -beamThermal $T_end $Y1 $T_end $Y2;
}
##Or should I only load element 5?

set Nstep 1;
set Factor [expr 1.0/$Nstep]; 	# first load increment;

constraints Plain;					# how it handles boundary conditions
numberer RCM;						# renumber dof's to minimize band-width (optimization)
#system BandGeneral;
system UmfPack;

test NormDispIncr 1e-8 1000;

#algorithm Newton;					
# algorithm NewtonLineSearch;
# algorithm BFGS;
# algorithm Broyden;
# algorithm KrylovNewton; 
# algorithm Linear;
# algorithm ModifiedNewton;
algorithm ExpressNewton 20;

integrator LoadControl $Factor;	# determine the next time step for an analysis
analysis Static;			# define type of analysis static or transient
analyze $Nstep;		# apply fire load


puts "Fire done"
