% Function to check if merging two triangles forms a convex polygon
function isConv = isConvexMergeOk(vertices, p1, p2)
    combined = unique([p1, p2]);
    k = convhull(vertices(combined, :));
    isConv = numel(k) == numel(combined) + 1;
end