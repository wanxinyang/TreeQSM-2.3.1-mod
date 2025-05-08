function xyz = read_ply(fn)
    fid = fopen(fn, 'r');
    if fid == -1
        error('Cannot open file: %s', fn);
    end

    tline = fgetl(fid); % read first line
    len = 0;
    prop = {};
    dtype = {};
    fmt = 'binary';

    while ~strcmp(tline, 'end_header')
        len = len + length(tline) + 1; % +1 for EOL

        tokens = strsplit(tline);
        if strcmp(tokens{1}, 'format') && strcmp(tokens{2}, 'ascii')
            fmt = 'ascii';
        elseif strcmp(tokens{1}, 'element') && strcmp(tokens{2}, 'vertex')
            N = str2double(tokens{3});
        elseif strcmp(tokens{1}, 'property')
            dtype{end+1} = tokens{2}; %#ok<AGROW>
            prop{end+1} = tokens{3}; %#ok<AGROW>
        end

        tline = fgetl(fid);
    end

    len = len + length(tline) + 1; % add 'end_header' line

    fseek(fid, 0, 'eof');
    file_length = ftell(fid) - len;
    fseek(fid, len, 'bof');

    types = struct('uchar', 1, 'float', 4, 'int', 4, 'float64', 8);
    pts = struct();
    seek_plus = 0;

    for i = 1:length(prop)
        fseek(fid, len + seek_plus, 'bof');
        dt = types.(dtype{i});
        stride = int32(file_length / N) - dt;
        pts.(prop{i}) = fread(fid, N, dtype{i}, stride);
        seek_plus = seek_plus + dt;
    end

    fclose(fid);

    if isfield(pts, 'label')
        xyz = [pts.x, pts.y, pts.z, pts.label];
    elseif isfield(pts, 'leaf')
        xyz = [pts.x, pts.y, pts.z, pts.leaf];
    else
        xyz = [pts.x, pts.y, pts.z];
    end
end