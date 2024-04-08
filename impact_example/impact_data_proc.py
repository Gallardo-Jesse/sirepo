from impact import Impact


def run_impact(fpath):
    I = Impact(fpath, verbose=True)
    I.numprocs = 1
    I.stop = 0.16
    I.run()
    return I.particles['final_particles'].x, I.particles['final_particles'].y


if __name__ == "__main__":
    x, y = run_impact('ImpactT.in')
    print("x =", x, "y =", y)
