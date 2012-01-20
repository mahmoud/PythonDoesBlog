${post.title}
${ '-' * len(post.title) }

PDW#${post.id} - ${post.author} - ${post.date}

${post.rst}


% if post.tags:
Tagged under:

.. class:: tags

   % for tag in post.tags:
   - ${tag | h}
   % endfor

% endif



