function clippedSegment = clipLineToPolygon(segment, polygon)
% Clip a line segment to a polygon using the
    clippedSegment = [];
    [xi, yi] = polyxpoly(segment(:,1), segment(:,2), polygon(:,1), polygon(:,2));
    if length(xi) == 2
        clippedSegment = [xi yi];
    end
end