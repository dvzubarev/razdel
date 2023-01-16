{
  description = "Razdel";
  inputs = {
    textapp-pkgs.url = "git+ssh://git@tsa04.isa.ru/textapp/textapp-pkgs";

  };

  outputs = { self, textapp-pkgs}:
    let pkgs = import textapp-pkgs.inputs.nixpkgs {
          system = "x86_64-linux";
          overlays = [ textapp-pkgs.overlays.default ];
          config.allowUnfree = true;
        };
        tlib = textapp-pkgs.lib;
        pypkgs = pkgs.python-torch.pkgs;
        tpkgs = textapp-pkgs.packages.x86_64-linux;
    in {

      devShells.x86_64-linux.default =
        pkgs.mkShell {
          # inputsFrom = [  ];
          buildInputs = [
            pypkgs.python
            pypkgs.pytest
            pypkgs.pytest-flakes
            tpkgs.pyright
            pypkgs.pylint
            pypkgs.ipykernel
          ];

          shellHook=''
          [ -n "$PS1" ] && setuptoolsShellHook
            '';

        };
    };

}
