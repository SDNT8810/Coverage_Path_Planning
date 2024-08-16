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
% Field_Params = Init_Field_Params([], 'triangle'      , 'No_Obstacle' , [0 0 0 0] , [-1 -1 0] , [3 8 0] , 0.5 , 5);
% Field_Params = Init_Field_Params([], 'quadrilateral' , 'No_Obstacle' , [0 0 0 0] , [3.5 -0.5 0] , [2.5 3.5 0] , 0.3 , 5);
% Field_Params = Init_Field_Params([], 'pentagonal'    , 'No_Obstacle' , [0 0 0 0] , [4 2 0] , [0 4 0] , 0.2 , 5);
% Field_Params = Init_Field_Params([], 'hexagonal'     , 'No_Obstacle' , [0 0 0 0] , [12 2 0] , [6 10 0] , 0.5 , 5);
% Field_Params = Init_Field_Params([], 'Non_Convac_1'  , 'No_Obstacle' , [0 0 0 0] , [35 25 0] , [15 28 0] , 1 , 5);
% Field_Params = Init_Field_Params([], 'Non_Convac_2'  , 'No_Obstacle' , [0 0 0 0] , [0 0 0] , [15 14 0] , 0.5 , 5);
% Field_Params = Init_Field_Params([], 'Non_Convac_3'  , 'No_Obstacle' , [0 0 0 0] , [0 0 0] , [15 14 0] , 0.5 , 5);
% Field_Params = Init_Field_Params([], 'Convac_1'      , 'No_Obstacle' , [0 0 0 0] , [14 0 0] , [10 12 0] , 0.5 , 5);
% Field_Params = Init_Field_Params([], 'Convac_2'      , 'No_Obstacle' , [0 0 0 0] , [10 1 0] , [6 10 0] , 0.5 , 5);

Blank_Field  = Init_Field_Params([], 'Blank'  , 'P_Obstacle' , [0 0 0 1] , [0 0 0] , [0 0 0] , 0 , 0);
% Field_Params = Init_Field_Params([], 'Non_Convac_1'  , 'No_Obstacle' , 0 , [35 25 0] , [15 28 0] , 0.7 , 5);
%Field_Params = Init_Field_Params([], 'Non_Convac_1' , 'P_Obstacle' , [8.5 6 1 1] , [9 10 0] , [8 0 0] , 1 , 5);
% Field_Params = Init_Field_Params([], 'Non_Convac_3'  , 'P_Obstacle' , [20 18 5 2] , [0 0 0] , [15 14 0] , 0.5 , 5);
%Field_Params = Init_Field_Params([], 'Non_Convac_2'  , 'No_Obstacle' , [16 16 0.5 2] , [30 15 0] , [17 3 0] , 2 , 5);
%Field_Params = Init_Field_Params([], 'Non_Convac_2'  , 'No_Obstacle' , [35 11 3 1] , [30 30 0] , [1 -1 0] , 3 , 5);
%Field_Params = Init_Field_Params([], 'Convac_2'      , 'R_Obstacle' , [7 5 1 2] , [14 0 0] , [10 12 0] , 0.5 , 5);
%Field_Params = Init_Field_Params([], 'triangle'      , 'P_Obstacle' , [5 5 1 1] , [-1 -1 0] , [0 23 0] , 3 , 5);
%Field_Params = Init_Field_Params([], 'quadrilateral' , 'No_Obstacle' , [0 0 0 0] , [3.5 -0.5 0] , [2.5 3.5 0] , 5 , 5);
%Field_Params = Init_Field_Params([], 'quadrilateral' , 'P_Obstacle' , [20 15 5 2] , [0 5 0] , [5 30 0] , 5 , 5);
%Field_Params = Init_Field_Params([], 'pentagonal'    , 'C_Obstacle' , [17 26 3.5 2] , [19 48 0] , [-2 6 0] , 0.2 , 5);
%Field_Params = Init_Field_Params([], 'hexagonal'     , 'C_Obstacle' , [35 15 5 1] , [55 10 0] , [45 5 0] , 5 , 5);
Field_Params = Init_Field_Params([], 'hexagonal'     , 'P_Obstacle' , [35 25 5 2] , [55 10 0] , [15 30 0] , 5 , 5);


% Show Field And Obstacle
figure(1);
Done = plotter(Field_Params,'V');
axis equal

% cut main polygon into small convex polygons (Decomposition)
polygons = Decomposition(Field_Params);
Region_Count = length(polygons);


%% Define State Variables
%(take off and landing points / theta / secuense)
DeCo_Ply{Region_Count} = [];
Seprated_Polygans{Region_Count} = [];
Order = randperm(Region_Count);
for i = 1 : Region_Count
    [Area, GeoCenter] = Area_Geo_Center(polygons{i}.Vertices);
    DeCo_Ply{i} = Blank_Field;
    DeCo_Ply{i}.Field_Polygon = polygons{i};
    DeCo_Ply{i}.Theta = 0;
    DeCo_Ply{i}.Order = Order(i);
    DeCo_Ply{i}.Area = Area;
    DeCo_Ply{i}.geocenter = GeoCenter;

    %{
    if (i == 1)
        DeCo_Ply{i}.takeoff = Field_Params.takeoff;
    elseif (i == Region_Count )
        DeCo_Ply{i}.takeoff = DeCo_Ply{i-1}.landing;
        DeCo_Ply{i}.landing = Field_Params.landing;
        
    else
        DeCo_Ply{i}.takeoff = DeCo_Ply{i-1}.landing;
        DeCo_Ply{i}.landing = Field_Params.landing;
    end
    %}

    Seprated_Polygans{i} = DeCo_Ply{i}.Field_Polygon.Vertices;
end


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

% Sumation of total path %%%%%%%%

% Make Next Generation

% Cost Function
% Objective function
% objective = @(theta) objectiveFunction(polygons, theta);

% Elimination


%% Optimizaition Algorithm
[Optimum_Path, Cost, LastGeneration] = GA_Optimizer(DeCo_Ply);

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

solve_Temporary;

