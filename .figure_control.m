function [save_path] = figure_control(repo, isfinal)
  if nargin < 2
    isfinal = false;
  end
  if isfinal
    [status, cmdout] = system(sprintf('{pypath} -f --repo="%s"', repo));
  else
    [status, cmdout] = system(sprintf('{pypath} --repo="%s"', repo));
  end
  strs = strsplit(cmdout, '\n');
  strs = strs(1:end-1);
  if numel(strs) > 1 && status == 0
    if contains(strs{1}, 'Created dir')
      disp(strs{1});
      save_path = strs{2};
    elseif contains(strs{1}, 'Your repo:')
      warning(strrep(strcat(strs{1:2}), sprintf('\t'), ' '));
      save_path = strs{end};
    end
  elseif status == 0
    save_path = strs{1};
  end
end % function
