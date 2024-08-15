function polygons = Decomposition(Field_Params)

    switch Field_Params.Obstacle(4)

        case 0
            polygons = PolygonDecomposition(Field_Params.Field_Polygon);
    
        case 1
            Obstacle_Unit = 0.5 * [-1 -1;-1 1;1 1;1 -1];
            Obstacle_Polygon = Obstacle_Unit * Field_Params.Obstacle(3) + Field_Params.Obstacle(1:2);
            polygons = Triangle_Merge_To_Polygon(Field_Params, Obstacle_Polygon);

        case 2

            Obstacle_Unit = 0.5 * [  1          0;
                                        0.7071     0.7071;
                                        0          1;
                                        -0.7071    0.7071;
                                        -1         0;
                                        -0.7071   -0.7071;
                                        0         -1;
                                        0.7071    -0.7071];

            Obstacle_Polygon = Obstacle_Unit * Field_Params.Obstacle(3) + Field_Params.Obstacle(1:2);
            polygons = Triangle_Merge_To_Polygon(Field_Params, Obstacle_Polygon);
    
        otherwise
            polygons{1} = Field_Params.Field_Polygon;

    end
end
