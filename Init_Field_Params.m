function Field_Params = Init_Field_Params(Vertices, Field_Type , Obstacle_Type , Obstacle ,  takeoff , landing , coverageWidth , uavElevation)
    
    %% Initializing parameters
    Field_Is_Blank = false;

    % Flight Parameters
    Field_Params.Field_Polygon = [];
    Field_Params.takeoff = takeoff;
    Field_Params.landing = landing;
    Field_Params.coverageWidth = coverageWidth;
    Field_Params.uavElevation = uavElevation;
    
    % Select Obstacle
    switch Obstacle_Type
        case 'No_Obstacle'
            disp('No Obstacle is on The Field.')
            disp(' ')
          % Field_Params.Obstacle --> [X, Y, Size, Type];
            Field_Params.Obstacle  =  Obstacle;
    
        case 'P_Obstacle'
            disp('Obstacle is a Polygonal Object')
            disp(' ')
          % Field_Params.Obstacle --> [X, Y, Size, Type];
            Field_Params.Obstacle  =  Obstacle;

        case 'C_Obstacle'
            disp('Obstacle is a Round Object')
            disp(' ')
          % Field_Params.Obstacle --> [X, Y, Size, Type];
            Field_Params.Obstacle  =  Obstacle;   
    
        otherwise
            disp('Undefined Obstacle Type')
            disp(' ')
          % Field_Params.Obstacle --> [X, Y, Size,Type];
            Field_Params.Obstacle  =  Obstacle;

    end


    % Select Field
    switch Field_Type
        case 'custom'
            Field_Polygon = Vertices;

        case 'triangle'
            triangle_vertices = 3*[0 0; 1 8; 7 0];
            Field_Polygon = triangle_vertices;
    
        case 'quadrilateral'
            quadrilateral_vertices = 10*[0 0; 1 3; 3 3; 4 0];
            Field_Polygon = quadrilateral_vertices;
            
        case 'pentagonal'
            pentagonal_vertices = 10*[0 0; 1 4; 3 5; 4 3; 2 0];
            Field_Polygon = pentagonal_vertices;
            
        case 'hexagonal'
            hexagonal_vertices = 5*[0 0; 4 6; 8 10; 12 8; 10 2; 6 0];
            Field_Polygon = hexagonal_vertices;

        case 'Convac_1'
            Convec_Polygon_1 = [2 0;12 0;14 8;7 12;0 6];
            Field_Polygon = Convec_Polygon_1;


        case 'Convac_2'
            Convec_Polygon_2 = [0 0; 4 6; 8 10; 12 8; 10 2; 6 0];
            Field_Polygon = Convec_Polygon_2;

            
        case 'Non_Convac_1'
            Non_Convec_Polygon_1 = [4 8.75; 4 27.5; 17.5 25.5; 25 31.25; 35 31.25; 30 20; 15 20];
            Field_Polygon = Non_Convec_Polygon_1;
            
        case 'Non_Convac_2'
            Non_Convec_Polygon_2 = 5*[2 0;12 0;14 15;7 4;0 6;2 0];
            Field_Polygon = Non_Convec_Polygon_2;

        case 'Non_Convac_3'
            Non_Convec_Polygon_3 = [5 8.75; 5 27.5; 17.5 22.5; 25 31.25; 35 31.25; 30 20; 15 6.25];
            Field_Polygon = Non_Convec_Polygon_3;

            
        otherwise
            disp('Undefined or Blank Field Type')
            disp(' ')
            Field_Polygon = [];
            Field_Is_Blank = true; 
            Field_Params.Area = 0;
            Field_Params.geocenter = [0 0 0];
    end

    Field_Params.Field_Polygon = Field_Polygon;
    if ~Field_Is_Blank
        [Area, GeoCenter] = Area_Geo_Center(Field_Params.Field_Polygon);
        Field_Params.Area = Area;
        Field_Params.geocenter = GeoCenter;
    end

    % Field_Params.Obstacle --> [X, Y, Size, Type];
    Field_Params.Obstacle  =  Obstacle;

end




