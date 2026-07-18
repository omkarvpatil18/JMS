% ============================================================
% instance_s1_disruption.lp -- Disruption variant: H1->D1 arc removed
% Corresponds to the disruption comparison table in Section 4.5
% Expected revised cost: 79 units (solver-verified optimal)
% The H1->D1 arc is removed to simulate carrier unavailability
% ============================================================

% Nodes (unchanged)
node(p1). node(p2).
node(h1). node(h2).
node(d1). node(d2).

% Directed arcs (H1->D1 removed)
edge(p1,h1). edge(p1,h2).
edge(p2,h1). edge(p2,h2).
% edge(h1,d1).  <-- REMOVED: carrier unavailability (Section 4.5)
edge(h1,d2).
edge(h2,d1). edge(h2,d2).

% Arc costs (unchanged from baseline)
cost(p1,h1,12). cost(p1,h2,18).
cost(p2,h1,15). cost(p2,h2,10).
cost(h1,d2,14).
cost(h2,d1,16). cost(h2,d2,9).

% Arc capacities (unchanged from baseline)
cap(p1,h1,20). cap(p1,h2,15).
cap(p2,h1,20). cap(p2,h2,25).
cap(h1,d2,20).
cap(h2,d1,15). cap(h2,d2,30).

% Shipment requests (unchanged)
ship(k1,p1,d1,8).
ship(k2,p2,d2,12).
ship(k3,p1,d2,6).
