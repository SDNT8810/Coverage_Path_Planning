% close all
clf
clear
clc

%% Define Field
% function Field_Params = Init_Field_Params(Vertices, Field_Type , Obstacle_Type , Obstacle_Size ,  takeoff , landing , coverageWidth , uavElevation)
% Initializing parameters (['custom' , 'triangle' , 'quadrilateral' , 'pentagonal' , 'hexagonal' , 'Non_Convac_1' , 'Non_Convac_2' , 'Convac_1' , 'Convac_2'] 
%                        , ['No_Obstacle' , 'P_Obstacle' , 'C_Obstacle'] , Obstacle_Size
%                        ,  takeoff , landing , coverageWidth , uavElevation)
%
%  Some Examples:
% Vertices = [0 0; 4 6; 8 10; 12 8; 10 2; 6 0; 0 0];
% Field_Params = Init_Field_Params(Vertices, 'custom'  , 'No_Obstacle' , [0 0 0 0] , [-1 -1 0] , [3 8 0] , 0.5 , 5);
% Field_Params = Init_Field_Params([], 'triangle'      , 'No_Obstacle' , [0 0 0 0], [-1 -1 0] , [0 23 0] , 3 , 5);
% Field_Params = Init_Field_Params([], 'quadrilateral' , 'No_Obstacle' , [0 0 0 0] , [0 5 0] , [5 30 0] , 5 , 5);
% Field_Params = Init_Field_Params([], 'pentagonal'    , 'No_Obstacle' , [0 0 0 0] , [4 2 0] , [0 4 0] , 0.2 , 5);
% Field_Params = Init_Field_Params([], 'hexagonal'     , 'No_Obstacle' , [0 0 0 0] , [12 2 0] , [6 10 0] , 0.5 , 5);
% Field_Params = Init_Field_Params([], 'Non_Convac_1'  , 'No_Obstacle' , [0 0 0 0] , [35 25 0] , [15 28 0] , 0.7 , 5);
% Field_Params = Init_Field_Params([], 'Non_Convac_2'  , 'No_Obstacle' , [0 0 0 0] , [0 0 0] , [15 14 0] , 0.5 , 5);
% Field_Params = Init_Field_Params([], 'Non_Convac_3'  , 'P_Obstacle' , [20 15 3 1] , [0 0 0] , [15 14 0] , 0.5 , 5);
% Field_Params = Init_Field_Params([], 'Convac_1'      , 'No_Obstacle' , [0 0 0 0] , [14 0 0] , [10 12 0] , 0.5 , 5);
% Field_Params = Init_Field_Params([], 'Convac_2'      , 'No_Obstacle' , [0 0 0 0] , [10 1 0] , [6 10 0] , 0.5 , 5);

Blank_Field  = Init_Field_Params([], 'Blank'  , 'No_Obstacle' , [0 0 0 0] , [0 0 0] , [0 0 0] , 0 , 0);
%Field_Params = Init_Field_Params([], 'Non_Convac_3'  , 'Po_Obstacle' , [20 15 1 2] , [30 15 0] , [5 7 0] , 1 , 5);
%Field_Params = Init_Field_Params([], 'hexagonal' , 'P_Obstacle' , [7.5 5 0.5 1] , [9 10 0] , [8 0 0] , 0.3 , 5);
Field_Params = Init_Field_Params([], 'Non_Convac_2'  , 'No_Obstacle' , [16 16 2 1] , [15 14 0] , [1 -1 0] , 2 , 5);

% Show Field And Obstacle
%figure(1);
%Done = plotter(Field_Params,'V');

% cut main polygon into small convex polygons (Decomposition)
polygons = Decomposition(Field_Params);
Region_Count = length(polygons);


%% Define State Variables
%(take off and landing points / theta / secuense)
% DeCo_Ply{Region_Count} = [];
% Seprated_Polygans{Region_Count} = [];
% Order = randperm(Region_Count);
% for i = 1 : Region_Count
%     [Area, GeoCenter] = Area_Geo_Center(polygons{i}.Vertices);
%     DeCo_Ply{i} = Blank_Field;
%     DeCo_Ply{i}.Field_Polygon = polygons{i};
%     DeCo_Ply{i}.Theta = 0;
%     DeCo_Ply{i}.Order = Order(i);
%     DeCo_Ply{i}.Area = Area;
%     DeCo_Ply{i}.geocenter = GeoCenter;
% 
%     %{
%     if (i == 1)
%         DeCo_Ply{i}.takeoff = Field_Params.takeoff;
%     elseif (i == Region_Count )
%         DeCo_Ply{i}.takeoff = DeCo_Ply{i-1}.landing;
%         DeCo_Ply{i}.landing = Field_Params.landing;
% 
%     else
%         DeCo_Ply{i}.takeoff = DeCo_Ply{i-1}.landing;
%         DeCo_Ply{i}.landing = Field_Params.landing;
%     end
%     %}
% 
%     Seprated_Polygans{i} = DeCo_Ply{i}.Field_Polygon.Vertices;
% end


%% Build Functions (To_Do_List):

% SWATH
%{
for i = 1 : Region_Count
    [Path, Start, End]   = SWATH_Convex_Polygon(DeCo_Ply{i}.Field_Polygon, Theta);
    DeCo_Ply{i}.Path = Path;
    DeCo_Ply{i}.takeoff = Start;
    DeCo_Ply{i}.landing = End;
end
%}

% Make Next Generation

% Cost Function
% Objective function
% objective = @(theta) objectiveFunction(polygons, theta);

% Elimination


%% Optimizaition Algorithm
%[Optimum_Path, Cost, LastGeneration] = GA_Optimizer(DeCo_Ply);

%{
X0 = [x0; y0; z0];  % Initial conditions for x, y, z

% Objective function
objective = @(x) objectiveFunction(x, alpha, beta, gamma);

% Set GA options
options = optimoptions('ga', ...
    'PopulationSize', 1000000, ...
    'MaxGenerations', 10000, ...
    'CrossoverFraction', 0.7, ...
    'MutationFcn', @mutationadaptfeasible, ...
    'Display', 'iter');

% Run GA
nvars = 3; % Number of variables [xt, yt, zt]
lb = 1000*[-10, -10, -10]; % Lower bounds
ub = 1000*[10, 10, 10]; % Upper bounds

[x, fval] = ga(objective, nvars, [], [], [], [], lb, ub, [], options);
%}

%% Report Results & Plots

cs = uavCoverageSpace(Polygons=polygons);
cpeExh = uavCoveragePlanner(cs,Solver="Exhaustive");
cpMin = uavCoveragePlanner(cs,Solver="MinTraversal");
%cpMin.SolverParameters.VisitingSequence =  [3 2 4 1];
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
% Seprated_Polygans = Field_Params.Field_Polygon;
% 
% csn = uavCoverageSpace(Polygons=Seprated_Polygans, ...
%                       UnitWidth=Field_Params.coverageWidth, ...
%                       ReferenceHeight=Field_Params.uavElevation, ...
%                       ReferenceLocation=Field_Params.geocenter);
% cp = uavCoveragePlanner(csn);
% 
% [waypoints,solnInfo] = cp.plan(Field_Params.landing, Field_Params.takeoff);


% Calculate the area
[Area, GeoCenter] = Area_Geo_Center(Field_Params.Field_Polygon);

% Display the area
disp(['The area of the polygon is ', num2str(Area), ' square meters']);
disp(' ')



% Plote
figure(1)
show(cs);
axis equal
PolygonPlotTakeoffLandingLegend(length(cs.Polygons),Field_Params.takeoff,Field_Params.landing)

figure(2)
show(cs);
axis equal
PolygonPlotTakeoffLandingLegend(length(cs.Polygons),Field_Params.takeoff,Field_Params.landing,wptsExh)

figure(3)
show(cs);
PolygonPlotTakeoffLandingLegend(length(cs.Polygons),Field_Params.takeoff,Field_Params.landing,wptsMin)
axis equal
% figure(4)
% show(cs);
% PolygonPlotTakeoffLandingLegend(length(cs.Polygons),Field_Params.takeoff,Field_Params.landing,waypoints)

axis equal


