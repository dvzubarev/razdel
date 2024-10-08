{
  description = "Razdel fork";
  inputs = {
    textapp-pkgs.url = "git+ssh://git@tsa04.isa.ru/textapp/textapp-pkgs";
  };
  outputs = { self, textapp-pkgs}:
    let pkgs = import textapp-pkgs.inputs.nixpkgs {
          system = "x86_64-linux";
          overlays = [ textapp-pkgs.overlays.default self.overlays.default ];
          config = textapp-pkgs.passthru.pkgs-config;
        };
        tlib = textapp-pkgs.lib;
        pypkgs = pkgs.python-torch.pkgs;
        tpkgs = textapp-pkgs.packages.x86_64-linux;

        python-overlay = pyfinal: pyprev: {razdel-fork = pyfinal.callPackage ./nix {src=self;};};
    in {

      overlays.default = final: prev: tlib.overrideAllPyVersions python-overlay prev;

      packages.x86_64-linux = tlib.allPyVersionsAttrSet {final-pkgs=pkgs;
                                                         default="razdel-fork";};

      devShells.x86_64-linux.default =
        pkgs.mkShell {
          buildInputs = [
            pkgs.pyright

            pypkgs.pytest
            pypkgs.pytest-flakes
            pypkgs.ipykernel

            pypkgs.pythonDevHook
          ];

        };
    };

}
