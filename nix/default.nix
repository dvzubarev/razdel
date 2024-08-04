{
  src,
  buildPythonPackage,
  pytest

}:
buildPythonPackage {
  pname = "razdel-fork";
  version = "0.6.1";
  inherit src;

  propagatedBuildInputs=[];
  nativeCheckInputs=[pytest];
  checkPhase="pytest razdel --int 0";
}
