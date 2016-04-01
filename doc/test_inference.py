#!/bin/env python

from graph_tool.all import *
import numpy.random
from numpy.random import randint

seed_rng(42)
numpy.random.seed(42)

graph_tool.inference.set_test(True)

g = collection.data["football"]
ec = g.new_ep("int", randint(0, 10, g.num_edges()))

def gen_state(directed, deg_corr, layers, overlap):
    u = GraphView(g, directed=directed)
    if layers != False:
        state = graph_tool.inference.LayeredBlockState(u, B=u.num_vertices(),
                                                       deg_corr=deg_corr,
                                                       ec=ec.copy(),
                                                       overlap=overlap,
                                                       layers=layers == True)
    elif overlap:
        state = graph_tool.inference.OverlapBlockState(u, B=2 * u.num_edges(),
                                                       deg_corr=deg_corr)
    else:
        state = graph_tool.inference.BlockState(u, B=u.num_vertices(),
                                                deg_corr=deg_corr)
    return state


for directed in [True, False]:
    for overlap in [False, True]:
        for layered in [False, "covariates", True]:
            for deg_corr in [False, True]:
                for dl in [False, True]:

                    print("\ndirected:", directed, "overlap:", overlap,
                          "layered:", layered, "deg-corr:", deg_corr, "dl:", dl)


                    print("\t mcmc (unweighted)")
                    state = gen_state(directed, deg_corr, layered, overlap)

                    print("\t\t", state.mcmc_sweep(beta=0, allow_empty=True,
                                                   entropy_args=dict(dl=dl)),
                          (state.wr.a > 0).sum())
                    if overlap:
                        print("\t\t", state.mcmc_sweep(beta=0, bundled=True,
                                                       allow_empty=True,
                                                       entropy_args=dict(dl=dl)),
                              (state.wr.a > 0).sum())

                    state = gen_state(directed, deg_corr, layered, overlap)

                    if not overlap:
                        print("\t mcmc")
                        bstate = state.get_block_state(vweight=True,
                                                       deg_corr=deg_corr)

                        print("\t\t",
                              bstate.mcmc_sweep(beta=0,
                                                allow_empty=True,
                                                entropy_args=dict(dl=dl,
                                                                  multigraph=False)),
                              (bstate.wr.a > 0).sum())

                        print("\t\t",
                              bstate.mcmc_sweep(beta=0, allow_empty=True,
                                                entropy_args=dict(dl=dl,
                                                                  multigraph=False)),
                              (bstate.wr.a > 0).sum())

                        print("\t\t",
                              bstate.gibbs_sweep(beta=0, allow_empty=True,
                                                 entropy_args=dict(dl=dl,
                                                                   multigraph=False)),
                              (bstate.wr.a > 0).sum())

                    print("\t merge")

                    state = gen_state(directed, deg_corr, layered, overlap)

                    if not overlap:
                        bstate = state.get_block_state(vweight=True,
                                                       deg_corr=deg_corr)

                        print("\t\t",
                              bstate.merge_sweep(50,
                                                 entropy_args=dict(dl=dl,
                                                                   multigraph=False)))

                        bstate = bstate.copy()

                        print("\t\t",
                              bstate.mcmc_sweep(beta=0, allow_empty=True,
                                                entropy_args=dict(dl=dl,
                                                                  multigraph=False)))
                        print("\t\t",
                              bstate.gibbs_sweep(beta=0, allow_empty=True,
                                                 entropy_args=dict(dl=dl,
                                                                multigraph=False)))
                    else:
                        print("\t\t",
                              state.merge_sweep(50,
                                                entropy_args=dict(dl=dl,
                                                                  multigraph=False)))

                    print("\t shrink")

                    state = gen_state(directed, deg_corr, layered, overlap)
                    state = state.shrink(B=5, entropy_args=dict(dl=dl,
                                                                multigraph=False))
                    print("\t\t", state.B)

for directed in [True, False]:
    for overlap in [False, True]:
        for layered in [False, "covariates", True]:
            for deg_corr in [False, True]:
                print("\ndirected:", directed, "overlap:", overlap,
                      "layered:", layered, "deg-corr:", deg_corr)

                state = minimize_blockmodel_dl(GraphView(g, directed=directed),
                                               verbose=(1, "\t"),
                                               deg_corr=deg_corr,
                                               overlap=overlap,
                                               layers=layered != False,
                                               state_args=dict(ec=ec,
                                                               layers=(layered == True)))
                print(state.B, state.entropy())

                state = minimize_nested_blockmodel_dl(GraphView(g, directed=directed),
                                                      verbose=(1, "\t"),
                                                      deg_corr=deg_corr,
                                                      overlap=overlap,
                                                      layers=layered != False,
                                                      state_args=dict(ec=ec,
                                                                      layers=(layered == True)))
                state.print_summary()
                print(state.entropy())
