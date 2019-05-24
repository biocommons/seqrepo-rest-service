seqrepo-rest-api
!!!!!!!!!!!!!!!!

Provides an OpenAPI-based REST interface to `seqrepo
<https://github.com/biocommons/biocommons.seqrepo/>`__.

Two APIs are now provided::

  * The refget (v1) interface, based on the `refget protocol
    <https://samtools.github.io/hts-specs/refget.html>`__.

  * The seqrepo interface, which provides more functionality than
    refget.

Both are based on OpenAPI.


.. important:: Everything is under development. Some instructions may
               be stale or broken.  Good luck. :-/



Development
@@@@@@@@@@@

$ make devready
$ source venv/3.7/bin/activate


Running a local instance
@@@@@@@@@@@@@@@@@@@@@@@@

Once installed as above, you should be able to::

  $ SEQREPO_DIR=/usr/local/share/seqrepo/latest seqrepo-rest-service

The navigate to the URL shown in the console output.


Running a docker image
@@@@@@@@@@@@@@@@@@@@@@

A docker image is available.  It expects to have a local seqrepo
instance installed.  Invoke like this::

  $ docker run --rm -t \
  -p 5000:5000 \
  -v /usr/local/share/seqrepo/:/usr/local/share/seqrepo/ \
  biocommons:seqrepo-rest-interface
