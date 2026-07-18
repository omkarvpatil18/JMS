% ============================================================
% instance_s1_greedy_comparison.lp
% Modified S1 instance for greedy vs ASP baseline comparison
% k3 quantity increased to 13t to trigger p1->h1 capacity breach
% Greedy sequential produces INFEASIBLE plan (21t > 20t cap)
% ASP optimal produces FEASIBLE plan at cost 66
% ============================================================

node(p1). node(p2). node(h1). node(h2). node(d1). node(d2).
edge(p1,h1). edge(p1,h2). edge(p2,h1). edge(p2,h2).
edge(h1,d1). edge(h1,d2). edge(h2,d1). edge(h2,d2).
cost(p1,h1,12). cost(p1,h2,18). cost(p2,h1,15). cost(p2,h2,10).
cost(h1,d1,8).  cost(h1,d2,14). cost(h2,d1,16). cost(h2,d2,9).
cap(p1,h1,20). cap(p1,h2,15). cap(p2,h1,20). cap(p2,h2,25).
cap(h1,d1,30). cap(h1,d2,20). cap(h2,d1,15). cap(h2,d2,30).
ship(k1,p1,d1,8).
ship(k2,p2,d2,12).
ship(k3,p1,d2,13).  %% increased from 6t to 13t for baseline comparison
