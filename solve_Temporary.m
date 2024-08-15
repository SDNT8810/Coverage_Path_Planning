cs = uavCoverageSpace(Polygons=Seprated_Polygans);
cpeExh = uavCoveragePlanner(cs,Solver="Exhaustive");
cpMin = uavCoveragePlanner(cs,Solver="MinTraversal");
cpMin.SolverParameters.VisitingSequence =  [3 2 4 1];
cpMin.SolverParameters.UnitWidth=Field_Params.coverageWidth;
cpMin.SolverParameters.ReferenceHeight=Field_Params.uavElevation;
cpMin.SolverParameters.ReferenceLocation=Field_Params.geocenter;


[wptsExh,solnExh] = plan(cpeExh,Field_Params.takeoff,Field_Params.landing);
[wptsMin,solnMin] = plan(cpMin ,Field_Params.takeoff,Field_Params.landing);

%{
setCoveragePattern(cs,1,SweepAngle=85)
setCoveragePattern(cs,2,SweepAngle=5)
setCoveragePattern(cs,3,SweepAngle=5)
setCoveragePattern(cs,4,SweepAngle=5)

cp = uavCoveragePlanner(cs,Solver="MinTraversal");

[wp,soln] = plan(cp,Field_Params.landing,Field_Params.takeoff);
legend("","","Path","Takeoff/Landing")
show(cp.CoverageSpace);
PolygonPlotTakeoffLandingLegend(length(cs.Polygons),Field_Params.takeoff,Field_Params.landing,wp)
%}



% 
% cpeExh = uavCoveragePlanner(cs,Solver="Exhaustive");
% cpMin = uavCoveragePlanner(cs,Solver="MinTraversal");
% % cpeExh.SolverParameters.VisitingSequence = [1 3 2];
% % cpMin.SolverParameters.VisitingSequence = [1 3 2];
% [wptsExh,solnExh] = plan(cpeExh,Field_Params.takeoff,Field_Params.landing);
% [wptsMin,solnMin] = plan(cpMin ,Field_Params.takeoff,Field_Params.landing);
% % plot(wptsExh(:,1),wptsExh(:,2))
% %plot(wptsMin(:,1),wptsMin(:,2))
% 
csn = uavCoverageSpace(Polygons=Seprated_Polygans, ...
                      UnitWidth=Field_Params.coverageWidth, ...
                      ReferenceHeight=Field_Params.uavElevation, ...
                      ReferenceLocation=Field_Params.geocenter);
cp = uavCoveragePlanner(csn);

[waypoints,solnInfo] = cp.plan(Field_Params.landing, Field_Params.takeoff);