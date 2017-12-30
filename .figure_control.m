function [save_path] = figure_control(repo, isfinal, conf_path)
  cmdstr = sprintf('{pypath} --repo="%s"', repo);
  if nargin < 2 || isempty(isfinal) || ~isfinal
    % do nothing
  else
    cmdstr = [cmdstr ' -f'];
  end
  if nargin == 3
    cmdstr = sprintf([cmdstr ' --config="%s"'], conf_path);
  end
  [status, cmdout] = system(cmdstr);
  strs = strsplit(cmdout, '\n');
  strs = strs(1:end-1);
  if numel(strs) > 1 && status == 0
    if contains(strs{1}, 'Your repo:')
      warning(strrep(strcat(strs{1:2}), sprintf('\t'), ' '));
    else
      fprintf([strjoin(strs{1:end-1}, '\n') '\n']);
    end
  end
  if status == 0
    save_path = strs{end};
  else
    warning('Error in figure-control call');
    disp(cmdout);
  end
end % function
