from pymarble.cli import main

def testSection():
  main([])
  # smart/automatic
  main(['','tests/examples/Membrane_Repeatability_05.mvl','m'])
  main(['','tests/examples/Membrane_Repeatability_05.mvl','s'])
  main(['','tests/examples/Membrane_Repeatability_05.mvl','z'])

  # find data
  main(['','tests/examples/Membrane_Repeatability_05.mvl','f'])
  main(['','tests/examples/Membrane_Repeatability_05.mvl','b'])
  main(['','tests/examples/Membrane_Repeatability_05.mvl','e'])

  # print information
  main(['','tests/examples/Membrane_Repeatability_05.mvl','p'])
  main(['','tests/examples/Membrane_Repeatability_05.mvl','a'])
  main(['','tests/examples/Membrane_Repeatability_05.mvl','g'])

  # read/write identified
  main(['','tests/examples/Membrane_Repeatability_05.mvl','r'])
  main(['','tests/examples/Membrane_Repeatability_05.mvl','d'])
  main(['','tests/examples/Membrane_Repeatability_05.mvl','y'])
  main(['','tests/examples/Membrane_Repeatability_05.mvl','t'])

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
  main(['','tests/examples/Membrane_Repeatability_05.mvl','abc']) #unknwon arg

