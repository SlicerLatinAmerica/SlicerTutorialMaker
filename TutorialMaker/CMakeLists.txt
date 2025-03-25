#-----------------------------------------------------------------------------
set(MODULE_NAME TutorialMaker)

#-----------------------------------------------------------------------------
set(MODULE_PYTHON_SCRIPTS
  ${MODULE_NAME}.py
  Lib/Annotations.py
  Lib/CreateTutorial.py
  Lib/GitTools.py
  Lib/TutorialEditor.py
  Lib/TutorialExporter.py
  Lib/TutorialGUI.py
  Lib/TutorialPainter.py
  Lib/utils.py
  )

file(GLOB_RECURSE MODULE_PYTHON_RESOURCES RELATIVE ${CMAKE_CURRENT_SOURCE_DIR}
  ${PROJECT_SOURCE_DIR}/Resources/Icons/*
  ${PROJECT_SOURCE_DIR}/Resources/UI/*
  ${PROJECT_SOURCE_DIR}/Resources/NewSlide/*
)

#-----------------------------------------------------------------------------
slicerMacroBuildScriptedModule(
  NAME ${MODULE_NAME}
  SCRIPTS ${MODULE_PYTHON_SCRIPTS}
  RESOURCES ${MODULE_PYTHON_RESOURCES}
  WITH_GENERIC_TESTS
  )

#-----------------------------------------------------------------------------
if(BUILD_TESTING)

  # Register the unittest subclass in the main script as a ctest.
  # Note that the test will also be available at runtime.
  slicer_add_python_unittest(SCRIPT ${MODULE_NAME}.py)

  # Additional build-time testing
  add_subdirectory(Testing)
endif()
