from impact import Impact
# import lume.base
# import rslume
I = Impact('ImpactT.in', verbose=True)
I.numprocs = 1
I.stop = 0.16
I.run()
x = I.particles['final_particles'].x
y = I.particles['final_particles'].y
print("x =", x, "y =", y)
