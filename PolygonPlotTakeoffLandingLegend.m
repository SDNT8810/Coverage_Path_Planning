function PolygonPlotTakeoffLandingLegend(varargin)
    N       = varargin{1};
    takeoff = varargin{2};
    landing = varargin{3};
    legend_string = [];
    
    hold on
    scatter(takeoff(1),takeoff(2),45,"filled")
    scatter(landing(1),landing(2),45,"filled")
    for i = 1 : N 
        NString = "Polygon " + num2str(i);
        legend_string = [legend_string ,NString];
    end
    legend_string = [legend_string,"Takeoff","Landing"];
    % If path is specified, then plot path and add that to legend
    if length(varargin) == 4
        path = varargin{4};
        plot(path(:,1),path(:,2),'b',LineWidth=1)
        legend_string = [legend_string , "Path"];
    end
    legend(legend_string, Location="best")
    xlabel('X(m)');
    ylabel('Y(m)');
    title('Polygon and Coverage Path');

    hold off

end