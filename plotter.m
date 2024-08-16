function done = plotter(Field_Params,type)

    Obstacle_Unit = 0.5 * [-1 -1;-1 1;1 1;1 -1];
    Obstacle_Unit = 0.5 * [  1          0;
                                        0.7071     0.7071;
                                        0          1;
                                        -0.7071    0.7071;
                                        -1         0;
                                        -0.7071   -0.7071;
                                        0         -1;
                                        0.7071    -0.707];
    Obstacle_Polygon = Obstacle_Unit * Field_Params.Obstacle(3) + Field_Params.Obstacle(1:2);
    Obstacle_Vertices = Obstacle_Polygon;
    uniqueVertices = unique(Field_Params.Field_Polygon, 'rows', 'stable');
    Plot_polygons{1} =  polyshape(uniqueVertices,'Simplify',false);
    uniqueVertices = unique(Obstacle_Vertices, 'rows', 'stable');
    Plot_polygons{2} =  polyshape(uniqueVertices,'Simplify',false);
    for i = 1 : 2
        ppp{i} = Plot_polygons{i}.Vertices;
    end
    cs = uavCoverageSpace(Polygons=ppp);
    show(cs);
    PolygonPlotTakeoffLandingLegend(length(cs.Polygons),Field_Params.takeoff,Field_Params.landing)
    
    done = type;

end