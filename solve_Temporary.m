cs = uavCoverageSpace(Polygons=Seprated_Polygans);
cpeExh = uavCoveragePlanner(cs,Solver="Exhaustive");
cpMin = uavCoveragePlanner(cs,Solver="MinTraversal");
%cpMin.SolverParameters.VisitingSequence =  [3 1 2 4];
%cpMin.SolverParameters.VisitingSequence =  [4 2 1 3];
cpMin.SolverParameters.UnitWidth=Field_Params.coverageWidth;
cpMin.SolverParameters.ReferenceHeight=Field_Params.uavElevation;
cpMin.SolverParameters.ReferenceLocation=Field_Params.geocenter;


[wptsExh,solnExh] = plan(cpeExh,Field_Params.takeoff,Field_Params.landing);
[wptsMin,solnMin] = plan(cpMin ,Field_Params.takeoff,Field_Params.landing);

%{
setCoveragePattern(cs,1,SweepAngle=0)
setCoveragePattern(cs,2,SweepAngle=25)
setCoveragePattern(cs,3,SweepAngle=55)
setCoveragePattern(cs,4,SweepAngle=-35)

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




% Calculate the area
[Area, GeoCenter] = Area_Geo_Center(Field_Params.Field_Polygon);

% Display the area
disp(['The area of the polygon is ', num2str(Area), ' square meters']);
disp(' ')

% Plote
figure(3)
show(cs);
axis equal

PolygonPlotTakeoffLandingLegend(length(cs.Polygons),Field_Params.takeoff,Field_Params.landing,wptsExh)

figure(5)
show(cs);
PolygonPlotTakeoffLandingLegend(length(cs.Polygons),Field_Params.takeoff,Field_Params.landing,wptsMin)
axis equal

figure(4)
show(cp.CoverageSpace);
PolygonPlotTakeoffLandingLegend(length(cs.Polygons),Field_Params.takeoff,Field_Params.landing,waypoints)

axis equal



