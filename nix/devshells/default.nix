# devShell definition for blueprint
# blueprint maps nix/devshells/default.nix to devShells.default
{ pkgs, ... }:
{
  default = import ../devshell.nix { inherit pkgs; };
}
