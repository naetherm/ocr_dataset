# Copyright 2019, University of Freiburg.
# Chair of Algorithms and Data Structures.
# Markus Näther <naetherm@informatik.uni-freiburg.de>

FROM ubuntu:19.10

MAINTAINER "Markus 'naetherm' Näther <naetherm@informatik.uni-freiburg.de>"

RUN mkdir /app/
WORKDIR /app/
COPY . /app/

VOLUME /data /output

# Install all dependencies
RUN ./install_deps.sh

# Install every package from CTAN
RUN tlmgr init-usertree
RUN TEXMFHOME=texmf TEXMFVAR=texmf-var updmap-user
RUN tlmgr update --self --all
RUN tlmgr install scheme-full

ENTRYPOINT ["/bin/bash"]

CMD ["./run.sh"]