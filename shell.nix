{
  pkgs ? import <nixpkgs> { },
}:
with pkgs;
mkShell {
  buildInputs = [
    nixpkgs-fmt
  ];
  packages = [
    virtualenv
    uv
  ];
  env = {
    UV_NO_SYNC = "1";
    UV_PYTHON = editablePythonSet.python.interpreter;
    UV_PYTHON_DOWNLOADS = "never";
  };

  shellHook = ''
    unset PYTHONPATH
    export REPO_ROOT=$(git rev-parse --show-toplevel)
  '';

}
