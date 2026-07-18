% ============================================================
% instance_s1.lp -- Baseline instance: 6 nodes, 8 arcs, 3 ships
% Corresponds to the transportation network table in Section 4
% Expected cost: 65 units (solver-verified optimal)
% ============================================================

% Nodes
node(p1). node(p2).  % production plants
node(h1). node(h2).  % consolidation hubs
node(d1). node(d2).  % delivery destinations

% Directed arcs
edge(p1,h1). edge(p1,h2).  % plant to hub
edge(p2,h1). edge(p2,h2).
edge(h1,d1). edge(h1,d2).  % hub to destination
edge(h2,d1). edge(h2,d2).

% Arc costs
cost(p1,h1,12). cost(p1,h2,18).
cost(p2,h1,15). cost(p2,h2,10).
cost(h1,d1,8).  cost(h1,d2,14).
cost(h2,d1,16). cost(h2,d2,9).

% Arc capacities in tonnes
cap(p1,h1,20). cap(p1,h2,15).
cap(p2,h1,20). cap(p2,h2,25).
cap(h1,d1,30). cap(h1,d2,20).
cap(h2,d1,15). cap(h2,d2,30).

% Shipment requests
ship(k1,p1,d1,8).   % 8 tonnes from P1 to D1
ship(k2,p2,d2,12).  % 12 tonnes from P2 to D2
ship(k3,p1,d2,6).   % 6 tonnes from P1 to D2
