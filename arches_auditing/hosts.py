import re
from django_hosts import patterns, host

host_patterns = patterns(
    "",
    host(re.sub(r"_", r"-", r"arches_auditing"), "arches_auditing.urls", name="arches_auditing"),
)