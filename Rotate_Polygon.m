function M = Rotate_Polygon(X,theta)

R = [cos(theta) -sin(theta);
    sin(theta)  cos(theta)];

M = (R * X')';
end