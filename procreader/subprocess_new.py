import subprocess
import os
import select

class Popen_events(subprocess.Popen):
  
  def __init__(self, args, bufsize=0, executable=None,
                 stdin=None, stdout=None, stderr=None,
                 preexec_fn=None, close_fds=False, shell=False,
                 cwd=None, env=None, universal_newlines=False,
                 startupinfo=None, creationflags=0, onStdOut=None, onStdErr=None):
    subprocess.Popen.__init__(self, args, bufsize, executable,
                     stdin, stdout, stderr,
                     preexec_fn, close_fds, shell,
                     cwd, env, universal_newlines,
                     startupinfo, creationflags)
    self.__onStdOut = onStdOut
    self.__onStdErr = onStdErr
    
  def _newCommunicate(self, input):
      read_set = []
      write_set = []
      stdout = None # Return
      stderr = None # Return

      if self.stdin:
          # Flush stdio buffer.  This might block, if the user has
          # been writing to .stdin in an uncontrolled fashion.
          self.stdin.flush()
          if input:
              write_set.append(self.stdin)
          else:
              self.stdin.close()
      if self.stdout:
          read_set.append(self.stdout)
          stdout = []
      if self.stderr:
          read_set.append(self.stderr)
          stderr = []

      input_offset = 0
      while read_set or write_set:
          try:
              rlist, wlist, xlist = select.select(read_set, write_set, [])
          except select.error, e:
              if e.args[0] == errno.EINTR:
                  continue
              raise

          if self.stdin in wlist:
              # When select has indicated that the file is writable,
              # we can write up to PIPE_BUF bytes without risk
              # blocking.  POSIX defines PIPE_BUF >= 512
              chunk = input[input_offset : input_offset + 512]
              bytes_written = os.write(self.stdin.fileno(), chunk)
              input_offset += bytes_written
              if input_offset >= len(input):
                  self.stdin.close()
                  write_set.remove(self.stdin)

          if self.stdout in rlist:
              data = self.stdout.readline()
              #data = os.read(self.stdout.fileno(), 1024)
              if data == "":
                  self.stdout.close()
                  read_set.remove(self.stdout)
              if self.__onStdOut != None:
                self.__onStdOut(data)
              #stdout.append(data)

          if self.stderr in rlist:
              data = self.stdout.readline()
              #data = os.read(self.stderr.fileno(), 1024)
              if data == "":
                  self.stderr.close()
                  read_set.remove(self.stderr)
              if self.__onStdErr != None:
                self.__onStdErr(data)
              #stderr.append(data)

      # All data exchanged.  Translate lists into strings.
      if stdout is not None:
          stdout = ''.join(stdout)
      if stderr is not None:
          stderr = ''.join(stderr)

      # Translate newlines, if requested.  We cannot let the file
      # object do the translation: It is based on stdio, which is
      # impossible to combine with select (unless forcing no
      # buffering).
      if self.universal_newlines and hasattr(file, 'newlines'):
          if stdout:
              stdout = self._translate_newlines(stdout)
          if stderr:
              stderr = self._translate_newlines(stderr)

      self.wait()
      return (stdout, stderr)
    
  def communicate(self, input=None):
    """Interact with process: Send data to stdin.  Read data from
    stdout and stderr, until end-of-file is reached.  Wait for
    process to terminate.  The optional input argument should be a
    string to be sent to the child process, or None, if no data
    should be sent to the child.

    communicate() returns a tuple (stdout, stderr)."""

    return self._newCommunicate(input)  

