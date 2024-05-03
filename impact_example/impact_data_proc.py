from impact import Impact


def run_impact(fpath):
    I = Impact(fpath, verbose=True)
    I.numprocs = 1
    I.stop = 0.16
    I.run()
    p = I.particles['final_particles']
    return p.x, p.y, p.px

if __name__ == "__main__":
    x, y, px = run_impact('ImpactT.in')
    print("x =", x, "y =", y, "px = ", px)
