function xyz = read_ply(fn)
    fid = fopen(fn, 'r');
    if fid == -1
        error('Could not open file: %s', fn);
    end

    tline = fgetl(fid); % Read first line

    len = 0;
    prop = {};
    dtype = {};
    fmt = 'binary';

    % Parse header
    while ~strcmp(tline, 'end_header')
        len = len + length(tline) + 1; % Include newline in header length

        tokens = strsplit(tline); % Split line into tokens
        if strcmp(tokens{1}, 'format') && strcmp(tokens{2}, 'ascii')
            fmt = 'ascii';
        elseif strcmp(tokens{1}, 'element') && strcmp(tokens{2}, 'vertex')
            N = str2double(tokens{3});
        elseif strcmp(tokens{1}, 'property')
            dtype = [dtype, tokens{2}];
            prop = [prop, tokens{3}];
        end
        tline = fgetl(fid);
    end

    len = len + length(tline) + 1; % Add 'end_header'

    % Total file length minus header
    fseek(fid, 0, 'eof');
    file_length = ftell(fid) - len;
    fseek(fid, len, 'bof');

    types = struct('uchar', 1, 'float', 4, 'int', 4, 'float64', 8);
    pts = struct();
    seek_plus = 0;

    for i = 1:length(prop)
        dt = types.(dtype{i}); % Bytes per value for this field
        fseek(fid, len + seek_plus, 'bof');
        pts.(prop{i}) = fread(fid, N, dtype{i}, int32(file_length / N) - dt);
        seek_plus = seek_plus + dt;
    end

    fclose(fid);

    % Assemble output
    if isfield(pts, 'label')
        xyz = [pts.x, pts.y, pts.z, pts.label];
    elseif isfield(pts, 'leaf')
        xyz = [pts.x, pts.y, pts.z, pts.leaf];
    else
        xyz = [pts.x, pts.y, pts.z];
    end
end
