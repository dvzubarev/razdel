{
  src,
  buildPythonPackage,
  pytest

}:
buildPythonPackage {
  pname = "razdel-fork";
  version = "0.6.0";
  inherit src;

  propagatedBuildInputs=[];
  checkInputs=[pytest];
  checkPhase="pytest razdel --int 0";
}
