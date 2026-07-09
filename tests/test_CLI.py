from pymarble.cli import main

def testSection(capsys):
  main([])
  # smart/automatic
  main(['','tests/examples/Membrane_Repeatability_05.mvl','m'])
  main(['','tests/examples/Membrane_Repeatability_05.mvl','sf 70840'])
  main(['','tests/examples/Membrane_Repeatability_05.mvl','z'])

  # find data
  main(['','tests/examples/Membrane_Repeatability_05.mvl','fi 195'])
  main(['','tests/examples/Membrane_Repeatability_05.mvl','bi 195'])
  # this is a test, not logical file processing. Since there is no sibling txt file for 05.mvl, use 08.mvl here
  main(['','tests/examples/Membrane_Repeatability_08.mvl','e tests/examples/Membrane_Repeatability_08.txt'])

  # print information
  main(['','tests/examples/Membrane_Repeatability_05.mvl','pi 1'])
  main(['','tests/examples/Membrane_Repeatability_05.mvl','a'])
  main(['','tests/examples/Membrane_Repeatability_05.mvl','g'])

  # read/write identified
  main(['','tests/examples/Membrane_Repeatability_05.mvl','r 0 1|i|test'])
  main(['','tests/examples/Membrane_Repeatability_05.mvl','d 0'])
  main(['','tests/examples/Membrane_Repeatability_05.mvl','m; y 69272'])
  main(['','tests/examples/Membrane_Repeatability_05.mvl','t 0 4 8'])

  # misc
  main(['','tests/examples/Membrane_Repeatability_05.mvl','x mode'])
  main(['','tests/examples/Membrane_Repeatability_05.mvl','ot'])
  main(['','tests/examples/Membrane_Repeatability_05.mvl','it'])
  main(['','tests/examples/Membrane_Repeatability_05.mvl','op'])
  main(['','tests/examples/Membrane_Repeatability_05.mvl','ip'])
  main(['','tests/examples/Membrane_Repeatability_05.mvl','x fill'])
  main(['','tests/examples/Membrane_Repeatability_05.mvl','x verify'])
  main(['','tests/examples/Membrane_Repeatability_05.mvl','q'])
  main(['','tests/examples/Membrane_Repeatability_05.mvl','h'])

  #errors
  main(['','tests/examples/Membrane_Repeatability_05.mvl','abc']) #unknown arg

  captured = capsys.readouterr()
  assert '**ERROR occurred' not in captured.out
  assert 'Traceback' not in captured.out
