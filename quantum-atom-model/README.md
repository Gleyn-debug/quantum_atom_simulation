QUANTUM ATOM MODEL
## Overview 
The user can change the three quantum numbers n,l,m and can observe how the shape and orientation of the orbital changes. 

## How the simulation work 

Principal Quantum number - n (N in the code) represents the main energy level of the electron. In the simulation values from n = 1 to n = 10 can be selected.
Angular Momentum Quantum Number - l labels subshells notation. 
For example: l = 0 → s 
                      l = 1 → p 
                      l = 2 → d and so on
Changing “l” determines the allowed states of  Magnetic Quantum Number - m ,which affects the angular distribution and orientation of a displayed orbital.

Schrödinger Equation gives the allowed stationary states and their energies, which tells us things like 
-which energy levels are allowed 
-possible subshells like s,p,d,f
-how probability distribution varies around the nucleus 
- n,l,m associated with each quantum state.
In here we used time-independent Schrödinger equation and it describes the stationary states. By solving the equation in spherical coordinates we separate the wavefunction into two components - angular and radial.

Radial Component

The radial_wave() function calculates the radial part of the wavefunction. 
It uses -> exponential decay, a power of radial coordinate and an associated Laguerre polynomial, which we calculate by calling associated_laguere ().

The the radial probability is treated proportional to r² × |R(r)|² 
Then the program uses rejection sampling to generate radius values according to the probability distribution.

Angular Component 

This angular_wave() basically determines how probability varies with direction. We calculate the associated Legendre polynomials using the associated_legendre()function.
The angular probability is then used to randomly sample directions in 3D space. 

Generating Electron Clouds

The generateClouds() function generates 10,000 points for a selected orbital. For every point  the program samples: 
Find an approximate max value of the radial probability distribution 
Randomly chooses a possible radius 
Calculates the probability at that radius 
Uses rejection sampling to decide whether the radius should be accepted. 
Repeats similar step for angular direction 
Converts the accepted radius and direction to x,y,z
Stores the point 

The program also calculates the sign of wavefunction at each point. Wavefunction = angular part x radial part. If the calculated wavefunction is positive then it is stored as a positive phase and given a unique color. The same process applies to negative wavefunction aka negative phase. 

3D Visualization

The simulation uses coordinate rotation and perspective projection. The user can left click and rotate. The user cal also zoom in or out by adjusting the mousewheel. 

Limitations

The points in this model represent randomly sampled possible electron positions based on the orbital probability distribution. An individual point should not be interpreted as an electron. Instead, the overall density of points represents where the electron is more or less likely to be found. 

