function f = objectiveFunction(polygons, theta)
    xt = polygons{1};


    
    if theta == 0
        f = inf;
        return;
    end

    x_dot = xt;
    y_dot = 1;
    z_dot = 1;

    f = x_dot^2 + y_dot^2 + z_dot^2;
end