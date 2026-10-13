/* Auto-generated golden benchmark circuits for Schematic2DSN */
window.BENCHMARK_CIRCUITS = {
  "bandpass_filter": {
    "schema_version": "1.0",
    "design": {
      "name": "bandpass_filter",
      "page": 1,
      "units": "mils",
      "grid": 100
    },
    "components": [
      {
        "id": "R1",
        "symbol_class": "RESISTOR",
        "value": "50R",
        "unit": 1,
        "position": {
          "x": 3800.0,
          "y": 3000.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "A",
            "pos": {
              "x": 3700.0,
              "y": 3000.0
            },
            "net": "VIN"
          },
          {
            "number": "2",
            "function": "B",
            "pos": {
              "x": 3900.0,
              "y": 3000.0
            },
            "net": "MID_NODE"
          }
        ]
      },
      {
        "id": "L1",
        "symbol_class": "INDUCTOR",
        "value": "10uH",
        "unit": 1,
        "position": {
          "x": 4300.0,
          "y": 3000.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "A",
            "pos": {
              "x": 4200.0,
              "y": 3000.0
            },
            "net": "MID_NODE"
          },
          {
            "number": "2",
            "function": "B",
            "pos": {
              "x": 4400.0,
              "y": 3000.0
            },
            "net": "OUT"
          }
        ]
      },
      {
        "id": "C1",
        "symbol_class": "CAPACITOR",
        "value": "100pF",
        "unit": 1,
        "position": {
          "x": 4300.0,
          "y": 3300.0
        },
        "rotation": 90,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "PLUS",
            "pos": {
              "x": 4300.0,
              "y": 3400.0
            },
            "net": "OUT"
          },
          {
            "number": "2",
            "function": "MINUS",
            "pos": {
              "x": 4300.0,
              "y": 3200.0
            },
            "net": "GND"
          }
        ]
      },
      {
        "id": "VCC1",
        "symbol_class": "VCC",
        "value": "",
        "unit": 1,
        "position": {
          "x": 3600.0,
          "y": 3200.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "PWR",
            "pos": {
              "x": 3600.0,
              "y": 3100.0
            },
            "net": "VIN"
          }
        ]
      },
      {
        "id": "GND1",
        "symbol_class": "GROUND",
        "value": "",
        "unit": 1,
        "position": {
          "x": 4300.0,
          "y": 3500.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "PWR",
            "pos": {
              "x": 4300.0,
              "y": 3600.0
            },
            "net": "GND"
          }
        ]
      }
    ],
    "nets": [
      {
        "name": "VIN",
        "auto_named": false,
        "pins": [
          [
            "R1",
            "1"
          ],
          [
            "VCC1",
            "1"
          ]
        ],
        "labels": [
          {
            "text": "VIN",
            "pos": {
              "x": 3600.0,
              "y": 3200.0
            }
          }
        ]
      },
      {
        "name": "MID_NODE",
        "auto_named": true,
        "pins": [
          [
            "R1",
            "2"
          ],
          [
            "L1",
            "1"
          ]
        ],
        "labels": []
      },
      {
        "name": "OUT",
        "auto_named": false,
        "pins": [
          [
            "L1",
            "2"
          ],
          [
            "C1",
            "1"
          ]
        ],
        "labels": [
          {
            "text": "OUT",
            "pos": {
              "x": 4500.0,
              "y": 3000.0
            }
          }
        ]
      },
      {
        "name": "GND",
        "auto_named": false,
        "pins": [
          [
            "C1",
            "2"
          ],
          [
            "GND1",
            "1"
          ]
        ],
        "labels": []
      }
    ],
    "warnings": [],
    "metadata": {
      "source": "synthetic",
      "mode": "vector",
      "confidence": 1.0,
      "ocr_confidence": 1.0
    }
  },
  "bjt_astable": {
    "schema_version": "1.0",
    "design": {
      "name": "bjt_astable",
      "page": 1,
      "units": "mils",
      "grid": 100
    },
    "components": [
      {
        "id": "R1",
        "symbol_class": "RESISTOR",
        "value": "1k",
        "unit": 1,
        "position": {
          "x": 3800.0,
          "y": 2600.0
        },
        "rotation": 90,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "A",
            "pos": {
              "x": 3800.0,
              "y": 2700.0
            },
            "net": "VCC"
          },
          {
            "number": "2",
            "function": "B",
            "pos": {
              "x": 3800.0,
              "y": 2500.0
            },
            "net": "NET_C1"
          }
        ]
      },
      {
        "id": "R2",
        "symbol_class": "RESISTOR",
        "value": "47k",
        "unit": 1,
        "position": {
          "x": 4100.0,
          "y": 2600.0
        },
        "rotation": 90,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "A",
            "pos": {
              "x": 4100.0,
              "y": 2700.0
            },
            "net": "VCC"
          },
          {
            "number": "2",
            "function": "B",
            "pos": {
              "x": 4100.0,
              "y": 2500.0
            },
            "net": "NET_B1"
          }
        ]
      },
      {
        "id": "R3",
        "symbol_class": "RESISTOR",
        "value": "47k",
        "unit": 1,
        "position": {
          "x": 4400.0,
          "y": 2600.0
        },
        "rotation": 90,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "A",
            "pos": {
              "x": 4400.0,
              "y": 2700.0
            },
            "net": "VCC"
          },
          {
            "number": "2",
            "function": "B",
            "pos": {
              "x": 4400.0,
              "y": 2500.0
            },
            "net": "NET_B2"
          }
        ]
      },
      {
        "id": "R4",
        "symbol_class": "RESISTOR",
        "value": "1k",
        "unit": 1,
        "position": {
          "x": 4700.0,
          "y": 2600.0
        },
        "rotation": 90,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "A",
            "pos": {
              "x": 4700.0,
              "y": 2700.0
            },
            "net": "VCC"
          },
          {
            "number": "2",
            "function": "B",
            "pos": {
              "x": 4700.0,
              "y": 2500.0
            },
            "net": "NET_C2"
          }
        ]
      },
      {
        "id": "C1",
        "symbol_class": "CAPACITOR",
        "value": "10uF",
        "unit": 1,
        "position": {
          "x": 4000.0,
          "y": 2900.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "PLUS",
            "pos": {
              "x": 3900.0,
              "y": 2900.0
            },
            "net": "NET_C1"
          },
          {
            "number": "2",
            "function": "MINUS",
            "pos": {
              "x": 4100.0,
              "y": 2900.0
            },
            "net": "NET_B2"
          }
        ]
      },
      {
        "id": "C2",
        "symbol_class": "CAPACITOR",
        "value": "10uF",
        "unit": 1,
        "position": {
          "x": 4500.0,
          "y": 2900.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "PLUS",
            "pos": {
              "x": 4400.0,
              "y": 2900.0
            },
            "net": "NET_C2"
          },
          {
            "number": "2",
            "function": "MINUS",
            "pos": {
              "x": 4600.0,
              "y": 2900.0
            },
            "net": "NET_B1"
          }
        ]
      },
      {
        "id": "Q1",
        "symbol_class": "NPN",
        "value": "2N2222",
        "unit": 1,
        "position": {
          "x": 3900.0,
          "y": 3200.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "BASE",
            "pos": {
              "x": 3750.0,
              "y": 3200.0
            },
            "net": "NET_B1"
          },
          {
            "number": "2",
            "function": "COLLECTOR",
            "pos": {
              "x": 4000.0,
              "y": 3350.0
            },
            "net": "NET_C1"
          },
          {
            "number": "3",
            "function": "EMITTER",
            "pos": {
              "x": 4000.0,
              "y": 3050.0
            },
            "net": "GND"
          }
        ]
      },
      {
        "id": "Q2",
        "symbol_class": "NPN",
        "value": "2N2222",
        "unit": 1,
        "position": {
          "x": 4600.0,
          "y": 3200.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "BASE",
            "pos": {
              "x": 4450.0,
              "y": 3200.0
            },
            "net": "NET_B2"
          },
          {
            "number": "2",
            "function": "COLLECTOR",
            "pos": {
              "x": 4700.0,
              "y": 3350.0
            },
            "net": "NET_C2"
          },
          {
            "number": "3",
            "function": "EMITTER",
            "pos": {
              "x": 4700.0,
              "y": 3050.0
            },
            "net": "GND"
          }
        ]
      },
      {
        "id": "VCC1",
        "symbol_class": "VCC",
        "value": "",
        "unit": 1,
        "position": {
          "x": 4250.0,
          "y": 2400.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "PWR",
            "pos": {
              "x": 4250.0,
              "y": 2300.0
            },
            "net": "VCC"
          }
        ]
      },
      {
        "id": "GND1",
        "symbol_class": "GROUND",
        "value": "",
        "unit": 1,
        "position": {
          "x": 4250.0,
          "y": 3500.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "PWR",
            "pos": {
              "x": 4250.0,
              "y": 3600.0
            },
            "net": "GND"
          }
        ]
      }
    ],
    "nets": [
      {
        "name": "VCC",
        "auto_named": false,
        "pins": [
          [
            "R1",
            "1"
          ],
          [
            "R2",
            "1"
          ],
          [
            "R3",
            "1"
          ],
          [
            "R4",
            "1"
          ],
          [
            "VCC1",
            "1"
          ]
        ],
        "labels": []
      },
      {
        "name": "NET_C1",
        "auto_named": true,
        "pins": [
          [
            "R1",
            "2"
          ],
          [
            "Q1",
            "2"
          ],
          [
            "C1",
            "1"
          ]
        ],
        "labels": []
      },
      {
        "name": "NET_B1",
        "auto_named": true,
        "pins": [
          [
            "R2",
            "2"
          ],
          [
            "Q1",
            "1"
          ],
          [
            "C2",
            "2"
          ]
        ],
        "labels": []
      },
      {
        "name": "NET_B2",
        "auto_named": true,
        "pins": [
          [
            "R3",
            "2"
          ],
          [
            "Q2",
            "1"
          ],
          [
            "C1",
            "2"
          ]
        ],
        "labels": []
      },
      {
        "name": "NET_C2",
        "auto_named": true,
        "pins": [
          [
            "R4",
            "2"
          ],
          [
            "Q2",
            "2"
          ],
          [
            "C2",
            "1"
          ]
        ],
        "labels": []
      },
      {
        "name": "GND",
        "auto_named": false,
        "pins": [
          [
            "Q1",
            "3"
          ],
          [
            "Q2",
            "3"
          ],
          [
            "GND1",
            "1"
          ]
        ],
        "labels": []
      }
    ],
    "warnings": [],
    "metadata": {
      "source": "synthetic",
      "mode": "vector",
      "confidence": 1.0,
      "ocr_confidence": 1.0
    }
  },
  "buck_converter": {
    "schema_version": "1.0",
    "design": {
      "name": "buck_converter",
      "page": 1,
      "units": "mils",
      "grid": 100
    },
    "components": [
      {
        "id": "U1",
        "symbol_class": "REGULATOR",
        "value": "LM2596-ADJ",
        "unit": 1,
        "sub_unit": null,
        "package": "TO-263-5",
        "description": "Step-Down Voltage Regulator",
        "position": {
          "x": 4200.0,
          "y": 3000.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "VIN",
            "pos": {
              "x": 4050.0,
              "y": 3060.0
            },
            "net": "VIN",
            "electrical_type": "POWER",
            "side": "LEFT"
          },
          {
            "number": "2",
            "function": "OUT",
            "pos": {
              "x": 4350.0,
              "y": 3060.0
            },
            "net": "SW_NODE",
            "electrical_type": "OUTPUT",
            "side": "RIGHT"
          },
          {
            "number": "3",
            "function": "GND",
            "pos": {
              "x": 4200.0,
              "y": 2880.0
            },
            "net": "GND",
            "electrical_type": "POWER",
            "side": "BOTTOM"
          },
          {
            "number": "4",
            "function": "FB",
            "pos": {
              "x": 4350.0,
              "y": 2960.0
            },
            "net": "FB_NODE",
            "electrical_type": "INPUT",
            "side": "RIGHT"
          },
          {
            "number": "5",
            "function": "ON_OFF",
            "pos": {
              "x": 4050.0,
              "y": 2960.0
            },
            "net": "GND",
            "electrical_type": "INPUT",
            "side": "LEFT"
          }
        ]
      },
      {
        "id": "CIN",
        "symbol_class": "CAPACITOR",
        "value": "100uF",
        "unit": 1,
        "sub_unit": null,
        "package": null,
        "description": null,
        "position": {
          "x": 3700.0,
          "y": 3000.0
        },
        "rotation": 90,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "PLUS",
            "pos": {
              "x": 3700.0,
              "y": 3100.0
            },
            "net": "VIN",
            "electrical_type": null,
            "side": null
          },
          {
            "number": "2",
            "function": "MINUS",
            "pos": {
              "x": 3700.0,
              "y": 2900.0
            },
            "net": "GND",
            "electrical_type": null,
            "side": null
          }
        ]
      },
      {
        "id": "D1",
        "symbol_class": "DIODE",
        "value": "1N5822",
        "unit": 1,
        "sub_unit": null,
        "package": null,
        "description": null,
        "position": {
          "x": 4450.0,
          "y": 2750.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "ANODE",
            "pos": {
              "x": 4350.0,
              "y": 2750.0
            },
            "net": "GND",
            "electrical_type": null,
            "side": null
          },
          {
            "number": "2",
            "function": "CATHODE",
            "pos": {
              "x": 4550.0,
              "y": 2750.0
            },
            "net": "SW_NODE",
            "electrical_type": null,
            "side": null
          }
        ]
      },
      {
        "id": "L1",
        "symbol_class": "INDUCTOR",
        "value": "33uH",
        "unit": 1,
        "sub_unit": null,
        "package": null,
        "description": null,
        "position": {
          "x": 4700.0,
          "y": 3060.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "A",
            "pos": {
              "x": 4600.0,
              "y": 3060.0
            },
            "net": "SW_NODE",
            "electrical_type": null,
            "side": null
          },
          {
            "number": "2",
            "function": "B",
            "pos": {
              "x": 4800.0,
              "y": 3060.0
            },
            "net": "VOUT",
            "electrical_type": null,
            "side": null
          }
        ]
      },
      {
        "id": "COUT",
        "symbol_class": "CAPACITOR",
        "value": "220uF",
        "unit": 1,
        "sub_unit": null,
        "package": null,
        "description": null,
        "position": {
          "x": 5100.0,
          "y": 2800.0
        },
        "rotation": 90,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "PLUS",
            "pos": {
              "x": 5100.0,
              "y": 2900.0
            },
            "net": "VOUT",
            "electrical_type": null,
            "side": null
          },
          {
            "number": "2",
            "function": "MINUS",
            "pos": {
              "x": 5100.0,
              "y": 2700.0
            },
            "net": "GND",
            "electrical_type": null,
            "side": null
          }
        ]
      },
      {
        "id": "R1",
        "symbol_class": "RESISTOR",
        "value": "3.1k",
        "unit": 1,
        "sub_unit": null,
        "package": null,
        "description": null,
        "position": {
          "x": 4800.0,
          "y": 2600.0
        },
        "rotation": 90,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "A",
            "pos": {
              "x": 4800.0,
              "y": 2700.0
            },
            "net": "VOUT",
            "electrical_type": null,
            "side": null
          },
          {
            "number": "2",
            "function": "B",
            "pos": {
              "x": 4800.0,
              "y": 2500.0
            },
            "net": "FB_NODE",
            "electrical_type": null,
            "side": null
          }
        ]
      },
      {
        "id": "R2",
        "symbol_class": "RESISTOR",
        "value": "1.0k",
        "unit": 1,
        "sub_unit": null,
        "package": null,
        "description": null,
        "position": {
          "x": 4800.0,
          "y": 2300.0
        },
        "rotation": 90,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "A",
            "pos": {
              "x": 4800.0,
              "y": 2400.0
            },
            "net": "FB_NODE",
            "electrical_type": null,
            "side": null
          },
          {
            "number": "2",
            "function": "B",
            "pos": {
              "x": 4800.0,
              "y": 2200.0
            },
            "net": "GND",
            "electrical_type": null,
            "side": null
          }
        ]
      },
      {
        "id": "VCC1",
        "symbol_class": "VCC",
        "value": "",
        "unit": 1,
        "sub_unit": null,
        "package": null,
        "description": null,
        "position": {
          "x": 3700.0,
          "y": 3350.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "PWR",
            "pos": {
              "x": 3700.0,
              "y": 3250.0
            },
            "net": "VIN",
            "electrical_type": null,
            "side": null
          }
        ]
      },
      {
        "id": "GND1",
        "symbol_class": "GROUND",
        "value": "",
        "unit": 1,
        "sub_unit": null,
        "package": null,
        "description": null,
        "position": {
          "x": 4200.0,
          "y": 2200.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "PWR",
            "pos": {
              "x": 4200.0,
              "y": 2300.0
            },
            "net": "GND",
            "electrical_type": null,
            "side": null
          }
        ]
      }
    ],
    "nets": [
      {
        "name": "VIN",
        "auto_named": false,
        "pins": [
          [
            "VCC1",
            "1"
          ],
          [
            "CIN",
            "1"
          ],
          [
            "U1",
            "1"
          ]
        ],
        "labels": [
          {
            "text": "VIN_24V",
            "pos": {
              "x": 3650.0,
              "y": 3350.0
            }
          }
        ]
      },
      {
        "name": "SW_NODE",
        "auto_named": true,
        "pins": [
          [
            "U1",
            "2"
          ],
          [
            "D1",
            "2"
          ],
          [
            "L1",
            "1"
          ]
        ],
        "labels": []
      },
      {
        "name": "VOUT",
        "auto_named": false,
        "pins": [
          [
            "L1",
            "2"
          ],
          [
            "COUT",
            "1"
          ],
          [
            "R1",
            "1"
          ]
        ],
        "labels": [
          {
            "text": "VOUT_5V",
            "pos": {
              "x": 5150.0,
              "y": 3100.0
            }
          }
        ]
      },
      {
        "name": "FB_NODE",
        "auto_named": true,
        "pins": [
          [
            "R1",
            "2"
          ],
          [
            "R2",
            "1"
          ],
          [
            "U1",
            "4"
          ]
        ],
        "labels": []
      },
      {
        "name": "GND",
        "auto_named": false,
        "pins": [
          [
            "GND1",
            "1"
          ],
          [
            "CIN",
            "2"
          ],
          [
            "U1",
            "3"
          ],
          [
            "U1",
            "5"
          ],
          [
            "D1",
            "1"
          ],
          [
            "COUT",
            "2"
          ],
          [
            "R2",
            "2"
          ]
        ],
        "labels": [
          {
            "text": "GND",
            "pos": {
              "x": 4200.0,
              "y": 2200.0
            }
          }
        ]
      }
    ],
    "warnings": [],
    "metadata": {
      "source": "synthetic",
      "mode": "vector",
      "confidence": 1.0,
      "ocr_confidence": 1.0
    }
  },
  "common_emitter": {
    "schema_version": "1.0",
    "design": {
      "name": "common_emitter",
      "page": 1,
      "units": "mils",
      "grid": 100
    },
    "components": [
      {
        "id": "R1",
        "symbol_class": "RESISTOR",
        "value": "1k",
        "unit": 1,
        "position": {
          "x": 4300.0,
          "y": 2600.0
        },
        "rotation": 90,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "A",
            "pos": {
              "x": 4300.0,
              "y": 2700.0
            },
            "net": "VCC"
          },
          {
            "number": "2",
            "function": "B",
            "pos": {
              "x": 4300.0,
              "y": 2500.0
            },
            "net": "COLLECTOR"
          }
        ]
      },
      {
        "id": "R2",
        "symbol_class": "RESISTOR",
        "value": "100k",
        "unit": 1,
        "position": {
          "x": 3800.0,
          "y": 3000.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "A",
            "pos": {
              "x": 3700.0,
              "y": 3000.0
            },
            "net": "VIN"
          },
          {
            "number": "2",
            "function": "B",
            "pos": {
              "x": 3900.0,
              "y": 3000.0
            },
            "net": "BASE"
          }
        ]
      },
      {
        "id": "Q1",
        "symbol_class": "NPN",
        "value": "2N2222",
        "unit": 1,
        "position": {
          "x": 4300.0,
          "y": 3000.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "BASE",
            "pos": {
              "x": 4150.0,
              "y": 3000.0
            },
            "net": "BASE"
          },
          {
            "number": "2",
            "function": "COLLECTOR",
            "pos": {
              "x": 4400.0,
              "y": 2850.0
            },
            "net": "COLLECTOR"
          },
          {
            "number": "3",
            "function": "EMITTER",
            "pos": {
              "x": 4400.0,
              "y": 3150.0
            },
            "net": "GND"
          }
        ]
      },
      {
        "id": "VCC1",
        "symbol_class": "VCC",
        "value": "",
        "unit": 1,
        "position": {
          "x": 4300.0,
          "y": 2400.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "PWR",
            "pos": {
              "x": 4300.0,
              "y": 2300.0
            },
            "net": "VCC"
          }
        ]
      },
      {
        "id": "GND1",
        "symbol_class": "GROUND",
        "value": "",
        "unit": 1,
        "position": {
          "x": 4400.0,
          "y": 3300.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "PWR",
            "pos": {
              "x": 4400.0,
              "y": 3400.0
            },
            "net": "GND"
          }
        ]
      }
    ],
    "nets": [
      {
        "name": "VCC",
        "auto_named": false,
        "pins": [
          [
            "R1",
            "1"
          ],
          [
            "VCC1",
            "1"
          ]
        ],
        "labels": []
      },
      {
        "name": "COLLECTOR",
        "auto_named": true,
        "pins": [
          [
            "R1",
            "2"
          ],
          [
            "Q1",
            "2"
          ]
        ],
        "labels": []
      },
      {
        "name": "VIN",
        "auto_named": false,
        "pins": [
          [
            "R2",
            "1"
          ]
        ],
        "labels": [
          {
            "text": "VIN",
            "pos": {
              "x": 3700.0,
              "y": 3000.0
            }
          }
        ]
      },
      {
        "name": "BASE",
        "auto_named": true,
        "pins": [
          [
            "R2",
            "2"
          ],
          [
            "Q1",
            "1"
          ]
        ],
        "labels": []
      },
      {
        "name": "GND",
        "auto_named": false,
        "pins": [
          [
            "Q1",
            "3"
          ],
          [
            "GND1",
            "1"
          ]
        ],
        "labels": []
      }
    ],
    "warnings": [],
    "metadata": {
      "source": "synthetic",
      "mode": "vector",
      "confidence": 1.0,
      "ocr_confidence": 1.0
    }
  },
  "diff_amp": {
    "schema_version": "1.0",
    "design": {
      "name": "diff_amp",
      "page": 1,
      "units": "mils",
      "grid": 100
    },
    "components": [
      {
        "id": "R1",
        "symbol_class": "RESISTOR",
        "value": "10k",
        "unit": 1,
        "position": {
          "x": 3700.0,
          "y": 2900.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "A",
            "pos": {
              "x": 3600.0,
              "y": 2900.0
            },
            "net": "VIN_NEG"
          },
          {
            "number": "2",
            "function": "B",
            "pos": {
              "x": 3800.0,
              "y": 2900.0
            },
            "net": "IN_MINUS"
          }
        ]
      },
      {
        "id": "R2",
        "symbol_class": "RESISTOR",
        "value": "100k",
        "unit": 1,
        "position": {
          "x": 4400.0,
          "y": 2700.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "A",
            "pos": {
              "x": 4300.0,
              "y": 2700.0
            },
            "net": "IN_MINUS"
          },
          {
            "number": "2",
            "function": "B",
            "pos": {
              "x": 4500.0,
              "y": 2700.0
            },
            "net": "VOUT"
          }
        ]
      },
      {
        "id": "R3",
        "symbol_class": "RESISTOR",
        "value": "10k",
        "unit": 1,
        "position": {
          "x": 3700.0,
          "y": 3100.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "A",
            "pos": {
              "x": 3600.0,
              "y": 3100.0
            },
            "net": "VIN_POS"
          },
          {
            "number": "2",
            "function": "B",
            "pos": {
              "x": 3800.0,
              "y": 3100.0
            },
            "net": "IN_PLUS"
          }
        ]
      },
      {
        "id": "R4",
        "symbol_class": "RESISTOR",
        "value": "100k",
        "unit": 1,
        "position": {
          "x": 4200.0,
          "y": 3300.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "A",
            "pos": {
              "x": 4100.0,
              "y": 3300.0
            },
            "net": "IN_PLUS"
          },
          {
            "number": "2",
            "function": "B",
            "pos": {
              "x": 4300.0,
              "y": 3300.0
            },
            "net": "GND"
          }
        ]
      },
      {
        "id": "U1",
        "symbol_class": "OPAMP",
        "value": "TL072",
        "unit": 1,
        "position": {
          "x": 4200.0,
          "y": 3000.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "IN_MINUS",
            "pos": {
              "x": 4000.0,
              "y": 2900.0
            },
            "net": "IN_MINUS"
          },
          {
            "number": "2",
            "function": "IN_PLUS",
            "pos": {
              "x": 4000.0,
              "y": 3100.0
            },
            "net": "IN_PLUS"
          },
          {
            "number": "3",
            "function": "VS_PLUS",
            "pos": {
              "x": 4200.0,
              "y": 2800.0
            },
            "net": "VCC"
          },
          {
            "number": "4",
            "function": "VS_MINUS",
            "pos": {
              "x": 4200.0,
              "y": 3200.0
            },
            "net": "VEE"
          },
          {
            "number": "5",
            "function": "OUT",
            "pos": {
              "x": 4400.0,
              "y": 3000.0
            },
            "net": "VOUT"
          }
        ]
      },
      {
        "id": "VCC1",
        "symbol_class": "VCC",
        "value": "",
        "unit": 1,
        "position": {
          "x": 4200.0,
          "y": 2600.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "PWR",
            "pos": {
              "x": 4200.0,
              "y": 2500.0
            },
            "net": "VCC"
          }
        ]
      },
      {
        "id": "GND1",
        "symbol_class": "GROUND",
        "value": "",
        "unit": 1,
        "position": {
          "x": 4200.0,
          "y": 3500.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "PWR",
            "pos": {
              "x": 4200.0,
              "y": 3600.0
            },
            "net": "GND"
          }
        ]
      },
      {
        "id": "GND2",
        "symbol_class": "GROUND",
        "value": "",
        "unit": 1,
        "position": {
          "x": 4350.0,
          "y": 3500.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "PWR",
            "pos": {
              "x": 4350.0,
              "y": 3600.0
            },
            "net": "VEE"
          }
        ]
      }
    ],
    "nets": [
      {
        "name": "VIN_NEG",
        "auto_named": false,
        "pins": [
          [
            "R1",
            "1"
          ]
        ],
        "labels": [
          {
            "text": "VIN_NEG",
            "pos": {
              "x": 3600.0,
              "y": 2900.0
            }
          }
        ]
      },
      {
        "name": "VIN_POS",
        "auto_named": false,
        "pins": [
          [
            "R3",
            "1"
          ]
        ],
        "labels": [
          {
            "text": "VIN_POS",
            "pos": {
              "x": 3600.0,
              "y": 3100.0
            }
          }
        ]
      },
      {
        "name": "IN_MINUS",
        "auto_named": true,
        "pins": [
          [
            "R1",
            "2"
          ],
          [
            "R2",
            "1"
          ],
          [
            "U1",
            "1"
          ]
        ],
        "labels": []
      },
      {
        "name": "IN_PLUS",
        "auto_named": true,
        "pins": [
          [
            "R3",
            "2"
          ],
          [
            "R4",
            "1"
          ],
          [
            "U1",
            "2"
          ]
        ],
        "labels": []
      },
      {
        "name": "VOUT",
        "auto_named": false,
        "pins": [
          [
            "R2",
            "2"
          ],
          [
            "U1",
            "5"
          ]
        ],
        "labels": [
          {
            "text": "VOUT",
            "pos": {
              "x": 4500.0,
              "y": 3000.0
            }
          }
        ]
      },
      {
        "name": "VCC",
        "auto_named": false,
        "pins": [
          [
            "U1",
            "3"
          ],
          [
            "VCC1",
            "1"
          ]
        ],
        "labels": []
      },
      {
        "name": "VEE",
        "auto_named": false,
        "pins": [
          [
            "U1",
            "4"
          ],
          [
            "GND2",
            "1"
          ]
        ],
        "labels": []
      },
      {
        "name": "GND",
        "auto_named": false,
        "pins": [
          [
            "R4",
            "2"
          ],
          [
            "GND1",
            "1"
          ]
        ],
        "labels": []
      }
    ],
    "warnings": [],
    "metadata": {
      "source": "synthetic",
      "mode": "vector",
      "confidence": 1.0,
      "ocr_confidence": 1.0
    }
  },
  "h_bridge": {
    "schema_version": "1.0",
    "design": {
      "name": "h_bridge",
      "page": 1,
      "units": "mils",
      "grid": 100
    },
    "components": [
      {
        "id": "M1",
        "symbol_class": "NMOS",
        "value": "2N7000",
        "unit": 1,
        "position": {
          "x": 3800.0,
          "y": 3200.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "GATE",
            "pos": {
              "x": 3650.0,
              "y": 3200.0
            },
            "net": "CTRL_LO_L"
          },
          {
            "number": "2",
            "function": "DRAIN",
            "pos": {
              "x": 3900.0,
              "y": 3350.0
            },
            "net": "MOTOR_A"
          },
          {
            "number": "3",
            "function": "SOURCE",
            "pos": {
              "x": 3900.0,
              "y": 3050.0
            },
            "net": "GND"
          }
        ]
      },
      {
        "id": "M2",
        "symbol_class": "PMOS",
        "value": "IRF9540",
        "unit": 1,
        "position": {
          "x": 3800.0,
          "y": 2700.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "GATE",
            "pos": {
              "x": 3650.0,
              "y": 2700.0
            },
            "net": "CTRL_HI_L"
          },
          {
            "number": "2",
            "function": "DRAIN",
            "pos": {
              "x": 3900.0,
              "y": 2850.0
            },
            "net": "MOTOR_A"
          },
          {
            "number": "3",
            "function": "SOURCE",
            "pos": {
              "x": 3900.0,
              "y": 2550.0
            },
            "net": "VCC"
          }
        ]
      },
      {
        "id": "M3",
        "symbol_class": "NMOS",
        "value": "2N7000",
        "unit": 1,
        "position": {
          "x": 4600.0,
          "y": 3200.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "GATE",
            "pos": {
              "x": 4450.0,
              "y": 3200.0
            },
            "net": "CTRL_LO_R"
          },
          {
            "number": "2",
            "function": "DRAIN",
            "pos": {
              "x": 4700.0,
              "y": 3350.0
            },
            "net": "MOTOR_B"
          },
          {
            "number": "3",
            "function": "SOURCE",
            "pos": {
              "x": 4700.0,
              "y": 3050.0
            },
            "net": "GND"
          }
        ]
      },
      {
        "id": "M4",
        "symbol_class": "PMOS",
        "value": "IRF9540",
        "unit": 1,
        "position": {
          "x": 4600.0,
          "y": 2700.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "GATE",
            "pos": {
              "x": 4450.0,
              "y": 2700.0
            },
            "net": "CTRL_HI_R"
          },
          {
            "number": "2",
            "function": "DRAIN",
            "pos": {
              "x": 4700.0,
              "y": 2850.0
            },
            "net": "MOTOR_B"
          },
          {
            "number": "3",
            "function": "SOURCE",
            "pos": {
              "x": 4700.0,
              "y": 2550.0
            },
            "net": "VCC"
          }
        ]
      },
      {
        "id": "R1",
        "symbol_class": "RESISTOR",
        "value": "10k",
        "unit": 1,
        "position": {
          "x": 3600.0,
          "y": 2700.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "A",
            "pos": {
              "x": 3500.0,
              "y": 2700.0
            },
            "net": "VCC"
          },
          {
            "number": "2",
            "function": "B",
            "pos": {
              "x": 3700.0,
              "y": 2700.0
            },
            "net": "CTRL_HI_L"
          }
        ]
      },
      {
        "id": "R2",
        "symbol_class": "RESISTOR",
        "value": "10k",
        "unit": 1,
        "position": {
          "x": 3600.0,
          "y": 3200.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "A",
            "pos": {
              "x": 3500.0,
              "y": 3200.0
            },
            "net": "CTRL_LO_L"
          },
          {
            "number": "2",
            "function": "B",
            "pos": {
              "x": 3700.0,
              "y": 3200.0
            },
            "net": "GND"
          }
        ]
      },
      {
        "id": "R3",
        "symbol_class": "RESISTOR",
        "value": "10k",
        "unit": 1,
        "position": {
          "x": 4800.0,
          "y": 2700.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "A",
            "pos": {
              "x": 4700.0,
              "y": 2700.0
            },
            "net": "VCC"
          },
          {
            "number": "2",
            "function": "B",
            "pos": {
              "x": 4900.0,
              "y": 2700.0
            },
            "net": "CTRL_HI_R"
          }
        ]
      },
      {
        "id": "R4",
        "symbol_class": "RESISTOR",
        "value": "10k",
        "unit": 1,
        "position": {
          "x": 4800.0,
          "y": 3200.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "A",
            "pos": {
              "x": 4700.0,
              "y": 3200.0
            },
            "net": "CTRL_LO_R"
          },
          {
            "number": "2",
            "function": "B",
            "pos": {
              "x": 4900.0,
              "y": 3200.0
            },
            "net": "GND"
          }
        ]
      },
      {
        "id": "J1",
        "symbol_class": "CONNECTOR",
        "value": "HEADER_1X2",
        "unit": 1,
        "position": {
          "x": 4200.0,
          "y": 2950.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "P1",
            "pos": {
              "x": 4300.0,
              "y": 3000.0
            },
            "net": "MOTOR_A"
          },
          {
            "number": "2",
            "function": "P2",
            "pos": {
              "x": 4300.0,
              "y": 2900.0
            },
            "net": "MOTOR_B"
          }
        ]
      },
      {
        "id": "VCC1",
        "symbol_class": "VCC",
        "value": "",
        "unit": 1,
        "position": {
          "x": 4200.0,
          "y": 2400.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "PWR",
            "pos": {
              "x": 4200.0,
              "y": 2300.0
            },
            "net": "VCC"
          }
        ]
      },
      {
        "id": "GND1",
        "symbol_class": "GROUND",
        "value": "",
        "unit": 1,
        "position": {
          "x": 4200.0,
          "y": 3500.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "PWR",
            "pos": {
              "x": 4200.0,
              "y": 3600.0
            },
            "net": "GND"
          }
        ]
      }
    ],
    "nets": [
      {
        "name": "VCC",
        "auto_named": false,
        "pins": [
          [
            "M2",
            "3"
          ],
          [
            "M4",
            "3"
          ],
          [
            "R1",
            "1"
          ],
          [
            "R3",
            "1"
          ],
          [
            "VCC1",
            "1"
          ]
        ],
        "labels": []
      },
      {
        "name": "GND",
        "auto_named": false,
        "pins": [
          [
            "M1",
            "3"
          ],
          [
            "M3",
            "3"
          ],
          [
            "R2",
            "2"
          ],
          [
            "R4",
            "2"
          ],
          [
            "GND1",
            "1"
          ]
        ],
        "labels": []
      },
      {
        "name": "MOTOR_A",
        "auto_named": true,
        "pins": [
          [
            "M1",
            "2"
          ],
          [
            "M2",
            "2"
          ],
          [
            "J1",
            "1"
          ]
        ],
        "labels": []
      },
      {
        "name": "MOTOR_B",
        "auto_named": true,
        "pins": [
          [
            "M3",
            "2"
          ],
          [
            "M4",
            "2"
          ],
          [
            "J1",
            "2"
          ]
        ],
        "labels": []
      },
      {
        "name": "CTRL_HI_L",
        "auto_named": false,
        "pins": [
          [
            "M2",
            "1"
          ],
          [
            "R1",
            "2"
          ]
        ],
        "labels": [
          {
            "text": "CTRL_HI_L",
            "pos": {
              "x": 3600.0,
              "y": 2700.0
            }
          }
        ]
      },
      {
        "name": "CTRL_LO_L",
        "auto_named": false,
        "pins": [
          [
            "M1",
            "1"
          ],
          [
            "R2",
            "1"
          ]
        ],
        "labels": [
          {
            "text": "CTRL_LO_L",
            "pos": {
              "x": 3600.0,
              "y": 3200.0
            }
          }
        ]
      },
      {
        "name": "CTRL_HI_R",
        "auto_named": false,
        "pins": [
          [
            "M4",
            "1"
          ],
          [
            "R3",
            "2"
          ]
        ],
        "labels": [
          {
            "text": "CTRL_HI_R",
            "pos": {
              "x": 4800.0,
              "y": 2700.0
            }
          }
        ]
      },
      {
        "name": "CTRL_LO_R",
        "auto_named": false,
        "pins": [
          [
            "M3",
            "1"
          ],
          [
            "R4",
            "1"
          ]
        ],
        "labels": [
          {
            "text": "CTRL_LO_R",
            "pos": {
              "x": 4800.0,
              "y": 3200.0
            }
          }
        ]
      }
    ],
    "warnings": [],
    "metadata": {
      "source": "synthetic",
      "mode": "vector",
      "confidence": 1.0,
      "ocr_confidence": 1.0
    }
  },
  "inverting_opamp": {
    "schema_version": "1.0",
    "design": {
      "name": "inverting_opamp",
      "page": 1,
      "units": "mils",
      "grid": 100
    },
    "components": [
      {
        "id": "R1",
        "symbol_class": "RESISTOR",
        "value": "10k",
        "unit": 1,
        "position": {
          "x": 3800.0,
          "y": 3100.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "A",
            "pos": {
              "x": 3700.0,
              "y": 3100.0
            },
            "net": "VIN"
          },
          {
            "number": "2",
            "function": "B",
            "pos": {
              "x": 3900.0,
              "y": 3100.0
            },
            "net": "IN_MINUS"
          }
        ]
      },
      {
        "id": "R2",
        "symbol_class": "RESISTOR",
        "value": "100k",
        "unit": 1,
        "position": {
          "x": 4600.0,
          "y": 2800.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "A",
            "pos": {
              "x": 4500.0,
              "y": 2800.0
            },
            "net": "IN_MINUS"
          },
          {
            "number": "2",
            "function": "B",
            "pos": {
              "x": 4700.0,
              "y": 2800.0
            },
            "net": "VOUT"
          }
        ]
      },
      {
        "id": "U1",
        "symbol_class": "OPAMP",
        "value": "LM741",
        "unit": 1,
        "position": {
          "x": 4300.0,
          "y": 3000.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "IN_MINUS",
            "pos": {
              "x": 4100.0,
              "y": 3100.0
            },
            "net": "IN_MINUS"
          },
          {
            "number": "2",
            "function": "IN_PLUS",
            "pos": {
              "x": 4100.0,
              "y": 2900.0
            },
            "net": "GND"
          },
          {
            "number": "3",
            "function": "VS_PLUS",
            "pos": {
              "x": 4300.0,
              "y": 3200.0
            },
            "net": "VCC"
          },
          {
            "number": "4",
            "function": "VS_MINUS",
            "pos": {
              "x": 4300.0,
              "y": 2800.0
            },
            "net": "VEE"
          },
          {
            "number": "5",
            "function": "OUT",
            "pos": {
              "x": 4500.0,
              "y": 3000.0
            },
            "net": "VOUT"
          }
        ]
      },
      {
        "id": "VCC1",
        "symbol_class": "VCC",
        "value": "",
        "unit": 1,
        "position": {
          "x": 4200.0,
          "y": 3400.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "PWR",
            "pos": {
              "x": 4200.0,
              "y": 3300.0
            },
            "net": "VCC"
          }
        ]
      },
      {
        "id": "GND1",
        "symbol_class": "GROUND",
        "value": "",
        "unit": 1,
        "position": {
          "x": 4100.0,
          "y": 2700.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "PWR",
            "pos": {
              "x": 4100.0,
              "y": 2800.0
            },
            "net": "GND"
          }
        ]
      },
      {
        "id": "GND2",
        "symbol_class": "GROUND",
        "value": "",
        "unit": 1,
        "position": {
          "x": 4300.0,
          "y": 2600.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "PWR",
            "pos": {
              "x": 4300.0,
              "y": 2700.0
            },
            "net": "VEE"
          }
        ]
      }
    ],
    "nets": [
      {
        "name": "VIN",
        "auto_named": false,
        "pins": [
          [
            "R1",
            "1"
          ]
        ],
        "labels": [
          {
            "text": "VIN",
            "pos": {
              "x": 3700.0,
              "y": 3100.0
            }
          }
        ]
      },
      {
        "name": "IN_MINUS",
        "auto_named": true,
        "pins": [
          [
            "R1",
            "2"
          ],
          [
            "U1",
            "1"
          ],
          [
            "R2",
            "1"
          ]
        ],
        "labels": []
      },
      {
        "name": "GND",
        "auto_named": false,
        "pins": [
          [
            "U1",
            "2"
          ],
          [
            "GND1",
            "1"
          ]
        ],
        "labels": []
      },
      {
        "name": "VCC",
        "auto_named": false,
        "pins": [
          [
            "U1",
            "3"
          ],
          [
            "VCC1",
            "1"
          ]
        ],
        "labels": []
      },
      {
        "name": "VEE",
        "auto_named": false,
        "pins": [
          [
            "U1",
            "4"
          ],
          [
            "GND2",
            "1"
          ]
        ],
        "labels": []
      },
      {
        "name": "VOUT",
        "auto_named": false,
        "pins": [
          [
            "U1",
            "5"
          ],
          [
            "R2",
            "2"
          ]
        ],
        "labels": [
          {
            "text": "VOUT",
            "pos": {
              "x": 4700.0,
              "y": 3000.0
            }
          }
        ]
      }
    ],
    "warnings": [],
    "metadata": {
      "source": "synthetic",
      "mode": "vector",
      "confidence": 1.0,
      "ocr_confidence": 1.0
    }
  },
  "led_driver": {
    "schema_version": "1.0",
    "design": {
      "name": "led_driver",
      "page": 1,
      "units": "mils",
      "grid": 100
    },
    "components": [
      {
        "id": "R1",
        "symbol_class": "RESISTOR",
        "value": "330R",
        "unit": 1,
        "position": {
          "x": 4000.0,
          "y": 3000.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "A",
            "pos": {
              "x": 3900.0,
              "y": 3000.0
            },
            "net": "VCC"
          },
          {
            "number": "2",
            "function": "B",
            "pos": {
              "x": 4100.0,
              "y": 3000.0
            },
            "net": "NET_001"
          }
        ]
      },
      {
        "id": "D1",
        "symbol_class": "LED",
        "value": "RED",
        "unit": 1,
        "position": {
          "x": 4600.0,
          "y": 3000.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "ANODE",
            "pos": {
              "x": 4500.0,
              "y": 3000.0
            },
            "net": "NET_001"
          },
          {
            "number": "2",
            "function": "CATHODE",
            "pos": {
              "x": 4700.0,
              "y": 3000.0
            },
            "net": "GND"
          }
        ]
      },
      {
        "id": "VCC1",
        "symbol_class": "VCC",
        "value": "",
        "unit": 1,
        "position": {
          "x": 3800.0,
          "y": 3200.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "PWR",
            "pos": {
              "x": 3800.0,
              "y": 3100.0
            },
            "net": "VCC"
          }
        ]
      },
      {
        "id": "GND1",
        "symbol_class": "GROUND",
        "value": "",
        "unit": 1,
        "position": {
          "x": 4800.0,
          "y": 2800.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "PWR",
            "pos": {
              "x": 4800.0,
              "y": 2900.0
            },
            "net": "GND"
          }
        ]
      }
    ],
    "nets": [
      {
        "name": "VCC",
        "auto_named": false,
        "pins": [
          [
            "R1",
            "1"
          ],
          [
            "VCC1",
            "1"
          ]
        ],
        "labels": []
      },
      {
        "name": "NET_001",
        "auto_named": true,
        "pins": [
          [
            "R1",
            "2"
          ],
          [
            "D1",
            "1"
          ]
        ],
        "labels": []
      },
      {
        "name": "GND",
        "auto_named": false,
        "pins": [
          [
            "D1",
            "2"
          ],
          [
            "GND1",
            "1"
          ]
        ],
        "labels": []
      }
    ],
    "warnings": [],
    "metadata": {
      "source": "synthetic",
      "mode": "vector",
      "confidence": 1.0,
      "ocr_confidence": 1.0
    }
  },
  "mcu_minimum_system": {
    "schema_version": "1.0",
    "design": {
      "name": "mcu_minimum_system",
      "page": 1,
      "units": "mils",
      "grid": 100
    },
    "components": [
      {
        "id": "U1",
        "symbol_class": "MICROCONTROLLER",
        "value": "ATMEGA328P",
        "unit": 1,
        "sub_unit": null,
        "package": "DIP-28",
        "description": "8-bit AVR Microcontroller",
        "position": {
          "x": 4200.0,
          "y": 3000.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "RESET",
            "pos": {
              "x": 4020.0,
              "y": 3140.0
            },
            "net": "RESET_NET",
            "electrical_type": "INPUT",
            "side": "LEFT"
          },
          {
            "number": "2",
            "function": "PD0_RXD",
            "pos": {
              "x": 4020.0,
              "y": 3100.0
            },
            "net": "MCU_RX",
            "electrical_type": "BIDIRECTIONAL",
            "side": "LEFT"
          },
          {
            "number": "3",
            "function": "PD1_TXD",
            "pos": {
              "x": 4020.0,
              "y": 3060.0
            },
            "net": "MCU_TX",
            "electrical_type": "BIDIRECTIONAL",
            "side": "LEFT"
          },
          {
            "number": "7",
            "function": "VCC",
            "pos": {
              "x": 4020.0,
              "y": 3020.0
            },
            "net": "VCC",
            "electrical_type": "POWER",
            "side": "LEFT"
          },
          {
            "number": "8",
            "function": "GND",
            "pos": {
              "x": 4020.0,
              "y": 2980.0
            },
            "net": "GND",
            "electrical_type": "POWER",
            "side": "LEFT"
          },
          {
            "number": "9",
            "function": "XTAL1",
            "pos": {
              "x": 4020.0,
              "y": 2940.0
            },
            "net": "XTAL1_NET",
            "electrical_type": "INPUT",
            "side": "LEFT"
          },
          {
            "number": "10",
            "function": "XTAL2",
            "pos": {
              "x": 4020.0,
              "y": 2900.0
            },
            "net": "XTAL2_NET",
            "electrical_type": "OUTPUT",
            "side": "LEFT"
          },
          {
            "number": "19",
            "function": "PB5_SCK",
            "pos": {
              "x": 4380.0,
              "y": 3100.0
            },
            "net": "LED_DRIVE",
            "electrical_type": "BIDIRECTIONAL",
            "side": "RIGHT"
          },
          {
            "number": "20",
            "function": "AVCC",
            "pos": {
              "x": 4380.0,
              "y": 3060.0
            },
            "net": "VCC",
            "electrical_type": "POWER",
            "side": "RIGHT"
          },
          {
            "number": "21",
            "function": "AREF",
            "pos": {
              "x": 4380.0,
              "y": 3020.0
            },
            "net": "AREF_NET",
            "electrical_type": "INPUT",
            "side": "RIGHT"
          },
          {
            "number": "22",
            "function": "AGND",
            "pos": {
              "x": 4380.0,
              "y": 2980.0
            },
            "net": "GND",
            "electrical_type": "POWER",
            "side": "RIGHT"
          }
        ]
      },
      {
        "id": "R1",
        "symbol_class": "RESISTOR",
        "value": "10k",
        "unit": 1,
        "sub_unit": null,
        "package": null,
        "description": null,
        "position": {
          "x": 3800.0,
          "y": 3400.0
        },
        "rotation": 90,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "A",
            "pos": {
              "x": 3800.0,
              "y": 3500.0
            },
            "net": "VCC",
            "electrical_type": null,
            "side": null
          },
          {
            "number": "2",
            "function": "B",
            "pos": {
              "x": 3800.0,
              "y": 3300.0
            },
            "net": "RESET_NET",
            "electrical_type": null,
            "side": null
          }
        ]
      },
      {
        "id": "SW1",
        "symbol_class": "SWITCH",
        "value": "RESET_BTN",
        "unit": 1,
        "sub_unit": null,
        "package": "SPST-TACT",
        "description": null,
        "position": {
          "x": 3800.0,
          "y": 3140.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "COM",
            "pos": {
              "x": 3700.0,
              "y": 3140.0
            },
            "net": "RESET_NET",
            "electrical_type": "PASSIVE",
            "side": null
          },
          {
            "number": "2",
            "function": "NO",
            "pos": {
              "x": 3900.0,
              "y": 3140.0
            },
            "net": "GND",
            "electrical_type": "PASSIVE",
            "side": null
          }
        ]
      },
      {
        "id": "Y1",
        "symbol_class": "CRYSTAL",
        "value": "16MHz",
        "unit": 1,
        "sub_unit": null,
        "package": "HC-49S",
        "description": null,
        "position": {
          "x": 3750.0,
          "y": 2750.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "XTAL1",
            "pos": {
              "x": 3650.0,
              "y": 2750.0
            },
            "net": "XTAL1_NET",
            "electrical_type": "PASSIVE",
            "side": null
          },
          {
            "number": "2",
            "function": "XTAL2",
            "pos": {
              "x": 3850.0,
              "y": 2750.0
            },
            "net": "XTAL2_NET",
            "electrical_type": "PASSIVE",
            "side": null
          }
        ]
      },
      {
        "id": "C1",
        "symbol_class": "CAPACITOR",
        "value": "22pF",
        "unit": 1,
        "sub_unit": null,
        "package": null,
        "description": null,
        "position": {
          "x": 3650.0,
          "y": 2500.0
        },
        "rotation": 90,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "PLUS",
            "pos": {
              "x": 3650.0,
              "y": 2600.0
            },
            "net": "XTAL1_NET",
            "electrical_type": null,
            "side": null
          },
          {
            "number": "2",
            "function": "MINUS",
            "pos": {
              "x": 3650.0,
              "y": 2400.0
            },
            "net": "GND",
            "electrical_type": null,
            "side": null
          }
        ]
      },
      {
        "id": "C2",
        "symbol_class": "CAPACITOR",
        "value": "22pF",
        "unit": 1,
        "sub_unit": null,
        "package": null,
        "description": null,
        "position": {
          "x": 3850.0,
          "y": 2500.0
        },
        "rotation": 90,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "PLUS",
            "pos": {
              "x": 3850.0,
              "y": 2600.0
            },
            "net": "XTAL2_NET",
            "electrical_type": null,
            "side": null
          },
          {
            "number": "2",
            "function": "MINUS",
            "pos": {
              "x": 3850.0,
              "y": 2400.0
            },
            "net": "GND",
            "electrical_type": null,
            "side": null
          }
        ]
      },
      {
        "id": "C3",
        "symbol_class": "CAPACITOR",
        "value": "100nF",
        "unit": 1,
        "sub_unit": null,
        "package": null,
        "description": null,
        "position": {
          "x": 4020.0,
          "y": 2700.0
        },
        "rotation": 90,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "PLUS",
            "pos": {
              "x": 4020.0,
              "y": 2800.0
            },
            "net": "VCC",
            "electrical_type": null,
            "side": null
          },
          {
            "number": "2",
            "function": "MINUS",
            "pos": {
              "x": 4020.0,
              "y": 2600.0
            },
            "net": "GND",
            "electrical_type": null,
            "side": null
          }
        ]
      },
      {
        "id": "C4",
        "symbol_class": "CAPACITOR",
        "value": "100nF",
        "unit": 1,
        "sub_unit": null,
        "package": null,
        "description": null,
        "position": {
          "x": 4600.0,
          "y": 2700.0
        },
        "rotation": 90,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "PLUS",
            "pos": {
              "x": 4600.0,
              "y": 2800.0
            },
            "net": "AREF_NET",
            "electrical_type": null,
            "side": null
          },
          {
            "number": "2",
            "function": "MINUS",
            "pos": {
              "x": 4600.0,
              "y": 2600.0
            },
            "net": "GND",
            "electrical_type": null,
            "side": null
          }
        ]
      },
      {
        "id": "R2",
        "symbol_class": "RESISTOR",
        "value": "1k",
        "unit": 1,
        "sub_unit": null,
        "package": null,
        "description": null,
        "position": {
          "x": 4700.0,
          "y": 3100.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "A",
            "pos": {
              "x": 4600.0,
              "y": 3100.0
            },
            "net": "LED_DRIVE",
            "electrical_type": null,
            "side": null
          },
          {
            "number": "2",
            "function": "B",
            "pos": {
              "x": 4800.0,
              "y": 3100.0
            },
            "net": "LED_NET",
            "electrical_type": null,
            "side": null
          }
        ]
      },
      {
        "id": "D1",
        "symbol_class": "DIODE",
        "value": "LED_STAT",
        "unit": 1,
        "sub_unit": null,
        "package": null,
        "description": null,
        "position": {
          "x": 5000.0,
          "y": 3100.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "ANODE",
            "pos": {
              "x": 4900.0,
              "y": 3100.0
            },
            "net": "LED_NET",
            "electrical_type": null,
            "side": null
          },
          {
            "number": "2",
            "function": "CATHODE",
            "pos": {
              "x": 5100.0,
              "y": 3100.0
            },
            "net": "GND",
            "electrical_type": null,
            "side": null
          }
        ]
      },
      {
        "id": "J1",
        "symbol_class": "CONNECTOR",
        "value": "UART_HDR_1X4",
        "unit": 1,
        "sub_unit": null,
        "package": "HDR-1X4",
        "description": null,
        "position": {
          "x": 3400.0,
          "y": 3000.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "VCC",
            "pos": {
              "x": 3480.0,
              "y": 3090.0
            },
            "net": "VCC",
            "electrical_type": "POWER",
            "side": null
          },
          {
            "number": "2",
            "function": "TX",
            "pos": {
              "x": 3480.0,
              "y": 3030.0
            },
            "net": "MCU_RX",
            "electrical_type": "OUTPUT",
            "side": null
          },
          {
            "number": "3",
            "function": "RX",
            "pos": {
              "x": 3480.0,
              "y": 2970.0
            },
            "net": "MCU_TX",
            "electrical_type": "INPUT",
            "side": null
          },
          {
            "number": "4",
            "function": "GND",
            "pos": {
              "x": 3480.0,
              "y": 2910.0
            },
            "net": "GND",
            "electrical_type": "POWER",
            "side": null
          }
        ]
      },
      {
        "id": "VCC1",
        "symbol_class": "VCC",
        "value": "",
        "unit": 1,
        "sub_unit": null,
        "package": null,
        "description": null,
        "position": {
          "x": 3800.0,
          "y": 3600.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "PWR",
            "pos": {
              "x": 3800.0,
              "y": 3500.0
            },
            "net": "VCC",
            "electrical_type": null,
            "side": null
          }
        ]
      },
      {
        "id": "GND1",
        "symbol_class": "GROUND",
        "value": "",
        "unit": 1,
        "sub_unit": null,
        "package": null,
        "description": null,
        "position": {
          "x": 4200.0,
          "y": 2200.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "PWR",
            "pos": {
              "x": 4200.0,
              "y": 2300.0
            },
            "net": "GND",
            "electrical_type": null,
            "side": null
          }
        ]
      }
    ],
    "nets": [
      {
        "name": "VCC",
        "auto_named": false,
        "pins": [
          [
            "VCC1",
            "1"
          ],
          [
            "U1",
            "7"
          ],
          [
            "U1",
            "20"
          ],
          [
            "R1",
            "1"
          ],
          [
            "C3",
            "1"
          ],
          [
            "J1",
            "1"
          ]
        ],
        "labels": [
          {
            "text": "VCC_5V",
            "pos": {
              "x": 3800.0,
              "y": 3600.0
            }
          }
        ]
      },
      {
        "name": "GND",
        "auto_named": false,
        "pins": [
          [
            "GND1",
            "1"
          ],
          [
            "U1",
            "8"
          ],
          [
            "U1",
            "22"
          ],
          [
            "SW1",
            "2"
          ],
          [
            "C1",
            "2"
          ],
          [
            "C2",
            "2"
          ],
          [
            "C3",
            "2"
          ],
          [
            "C4",
            "2"
          ],
          [
            "D1",
            "2"
          ],
          [
            "J1",
            "4"
          ]
        ],
        "labels": [
          {
            "text": "GND",
            "pos": {
              "x": 4200.0,
              "y": 2200.0
            }
          }
        ]
      },
      {
        "name": "RESET_NET",
        "auto_named": false,
        "pins": [
          [
            "R1",
            "2"
          ],
          [
            "SW1",
            "1"
          ],
          [
            "U1",
            "1"
          ]
        ],
        "labels": [
          {
            "text": "RESET",
            "pos": {
              "x": 3750.0,
              "y": 3250.0
            }
          }
        ]
      },
      {
        "name": "XTAL1_NET",
        "auto_named": true,
        "pins": [
          [
            "U1",
            "9"
          ],
          [
            "Y1",
            "1"
          ],
          [
            "C1",
            "1"
          ]
        ],
        "labels": []
      },
      {
        "name": "XTAL2_NET",
        "auto_named": true,
        "pins": [
          [
            "U1",
            "10"
          ],
          [
            "Y1",
            "2"
          ],
          [
            "C2",
            "1"
          ]
        ],
        "labels": []
      },
      {
        "name": "AREF_NET",
        "auto_named": true,
        "pins": [
          [
            "U1",
            "21"
          ],
          [
            "C4",
            "1"
          ]
        ],
        "labels": []
      },
      {
        "name": "MCU_RX",
        "auto_named": false,
        "pins": [
          [
            "U1",
            "2"
          ],
          [
            "J1",
            "2"
          ]
        ],
        "labels": [
          {
            "text": "UART_RX",
            "pos": {
              "x": 3500.0,
              "y": 3100.0
            }
          }
        ]
      },
      {
        "name": "MCU_TX",
        "auto_named": false,
        "pins": [
          [
            "U1",
            "3"
          ],
          [
            "J1",
            "3"
          ]
        ],
        "labels": [
          {
            "text": "UART_TX",
            "pos": {
              "x": 3500.0,
              "y": 2900.0
            }
          }
        ]
      },
      {
        "name": "LED_DRIVE",
        "auto_named": true,
        "pins": [
          [
            "U1",
            "19"
          ],
          [
            "R2",
            "1"
          ]
        ],
        "labels": []
      },
      {
        "name": "LED_NET",
        "auto_named": true,
        "pins": [
          [
            "R2",
            "2"
          ],
          [
            "D1",
            "1"
          ]
        ],
        "labels": []
      }
    ],
    "warnings": [],
    "metadata": {
      "source": "synthetic",
      "mode": "vector",
      "confidence": 1.0,
      "ocr_confidence": 1.0
    }
  },
  "rc_filter": {
    "schema_version": "1.0",
    "design": {
      "name": "rc_filter",
      "page": 1,
      "units": "mils",
      "grid": 100
    },
    "components": [
      {
        "id": "R1",
        "symbol_class": "RESISTOR",
        "value": "1k",
        "unit": 1,
        "position": {
          "x": 4000.0,
          "y": 3000.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "A",
            "pos": {
              "x": 3900.0,
              "y": 3000.0
            },
            "net": "VCC"
          },
          {
            "number": "2",
            "function": "B",
            "pos": {
              "x": 4100.0,
              "y": 3000.0
            },
            "net": "OUT"
          }
        ]
      },
      {
        "id": "C1",
        "symbol_class": "CAPACITOR",
        "value": "100nF",
        "unit": 1,
        "position": {
          "x": 4600.0,
          "y": 3000.0
        },
        "rotation": 90,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "PLUS",
            "pos": {
              "x": 4600.0,
              "y": 3100.0
            },
            "net": "OUT"
          },
          {
            "number": "2",
            "function": "MINUS",
            "pos": {
              "x": 4600.0,
              "y": 2900.0
            },
            "net": "GND"
          }
        ]
      },
      {
        "id": "VCC1",
        "symbol_class": "VCC",
        "value": "",
        "unit": 1,
        "position": {
          "x": 3800.0,
          "y": 3200.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "PWR",
            "pos": {
              "x": 3800.0,
              "y": 3100.0
            },
            "net": "VCC"
          }
        ]
      },
      {
        "id": "GND1",
        "symbol_class": "GROUND",
        "value": "",
        "unit": 1,
        "position": {
          "x": 4800.0,
          "y": 2800.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "PWR",
            "pos": {
              "x": 4800.0,
              "y": 2900.0
            },
            "net": "GND"
          }
        ]
      }
    ],
    "nets": [
      {
        "name": "VCC",
        "auto_named": false,
        "pins": [
          [
            "R1",
            "1"
          ],
          [
            "VCC1",
            "1"
          ]
        ],
        "labels": []
      },
      {
        "name": "OUT",
        "auto_named": true,
        "pins": [
          [
            "R1",
            "2"
          ],
          [
            "C1",
            "1"
          ]
        ],
        "labels": []
      },
      {
        "name": "GND",
        "auto_named": false,
        "pins": [
          [
            "C1",
            "2"
          ],
          [
            "GND1",
            "1"
          ]
        ],
        "labels": []
      }
    ],
    "warnings": [],
    "metadata": {
      "source": "synthetic",
      "mode": "vector",
      "confidence": 1.0,
      "ocr_confidence": 1.0
    }
  },
  "timer_555_astable": {
    "schema_version": "1.0",
    "design": {
      "name": "timer_555_astable",
      "page": 1,
      "units": "mils",
      "grid": 100
    },
    "components": [
      {
        "id": "U1",
        "symbol_class": "TIMER_555",
        "value": "NE555",
        "unit": 1,
        "sub_unit": null,
        "package": "DIP-8",
        "description": "Precision Timer IC",
        "position": {
          "x": 4200.0,
          "y": 3000.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "GND",
            "pos": {
              "x": 4050.0,
              "y": 2910.0
            },
            "net": "GND",
            "electrical_type": "POWER",
            "side": "LEFT"
          },
          {
            "number": "2",
            "function": "TRIG",
            "pos": {
              "x": 4050.0,
              "y": 2970.0
            },
            "net": "TRIG_NODE",
            "electrical_type": "INPUT",
            "side": "LEFT"
          },
          {
            "number": "3",
            "function": "OUT",
            "pos": {
              "x": 4350.0,
              "y": 2970.0
            },
            "net": "OUT_NODE",
            "electrical_type": "OUTPUT",
            "side": "RIGHT"
          },
          {
            "number": "4",
            "function": "RESET",
            "pos": {
              "x": 4050.0,
              "y": 3090.0
            },
            "net": "VCC",
            "electrical_type": "INPUT",
            "side": "LEFT"
          },
          {
            "number": "5",
            "function": "CTRL",
            "pos": {
              "x": 4350.0,
              "y": 2910.0
            },
            "net": "CTRL_NODE",
            "electrical_type": "PASSIVE",
            "side": "RIGHT"
          },
          {
            "number": "6",
            "function": "THRESH",
            "pos": {
              "x": 4050.0,
              "y": 3030.0
            },
            "net": "TRIG_NODE",
            "electrical_type": "INPUT",
            "side": "LEFT"
          },
          {
            "number": "7",
            "function": "DISCH",
            "pos": {
              "x": 4350.0,
              "y": 3030.0
            },
            "net": "DISCH_NODE",
            "electrical_type": "OUTPUT",
            "side": "RIGHT"
          },
          {
            "number": "8",
            "function": "VCC",
            "pos": {
              "x": 4350.0,
              "y": 3090.0
            },
            "net": "VCC",
            "electrical_type": "POWER",
            "side": "RIGHT"
          }
        ]
      },
      {
        "id": "R1",
        "symbol_class": "RESISTOR",
        "value": "10k",
        "unit": 1,
        "sub_unit": null,
        "package": null,
        "description": null,
        "position": {
          "x": 4200.0,
          "y": 3400.0
        },
        "rotation": 90,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "A",
            "pos": {
              "x": 4200.0,
              "y": 3500.0
            },
            "net": "VCC",
            "electrical_type": null,
            "side": null
          },
          {
            "number": "2",
            "function": "B",
            "pos": {
              "x": 4200.0,
              "y": 3300.0
            },
            "net": "DISCH_NODE",
            "electrical_type": null,
            "side": null
          }
        ]
      },
      {
        "id": "R2",
        "symbol_class": "RESISTOR",
        "value": "47k",
        "unit": 1,
        "sub_unit": null,
        "package": null,
        "description": null,
        "position": {
          "x": 3800.0,
          "y": 3200.0
        },
        "rotation": 90,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "A",
            "pos": {
              "x": 3800.0,
              "y": 3300.0
            },
            "net": "DISCH_NODE",
            "electrical_type": null,
            "side": null
          },
          {
            "number": "2",
            "function": "B",
            "pos": {
              "x": 3800.0,
              "y": 3100.0
            },
            "net": "TRIG_NODE",
            "electrical_type": null,
            "side": null
          }
        ]
      },
      {
        "id": "C1",
        "symbol_class": "CAPACITOR",
        "value": "10uF",
        "unit": 1,
        "sub_unit": null,
        "package": null,
        "description": null,
        "position": {
          "x": 3800.0,
          "y": 2600.0
        },
        "rotation": 90,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "PLUS",
            "pos": {
              "x": 3800.0,
              "y": 2700.0
            },
            "net": "TRIG_NODE",
            "electrical_type": null,
            "side": null
          },
          {
            "number": "2",
            "function": "MINUS",
            "pos": {
              "x": 3800.0,
              "y": 2500.0
            },
            "net": "GND",
            "electrical_type": null,
            "side": null
          }
        ]
      },
      {
        "id": "C2",
        "symbol_class": "CAPACITOR",
        "value": "10nF",
        "unit": 1,
        "sub_unit": null,
        "package": null,
        "description": null,
        "position": {
          "x": 4600.0,
          "y": 2600.0
        },
        "rotation": 90,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "PLUS",
            "pos": {
              "x": 4600.0,
              "y": 2700.0
            },
            "net": "CTRL_NODE",
            "electrical_type": null,
            "side": null
          },
          {
            "number": "2",
            "function": "MINUS",
            "pos": {
              "x": 4600.0,
              "y": 2500.0
            },
            "net": "GND",
            "electrical_type": null,
            "side": null
          }
        ]
      },
      {
        "id": "R3",
        "symbol_class": "RESISTOR",
        "value": "330R",
        "unit": 1,
        "sub_unit": null,
        "package": null,
        "description": null,
        "position": {
          "x": 4700.0,
          "y": 2970.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "A",
            "pos": {
              "x": 4600.0,
              "y": 2970.0
            },
            "net": "OUT_NODE",
            "electrical_type": null,
            "side": null
          },
          {
            "number": "2",
            "function": "B",
            "pos": {
              "x": 4800.0,
              "y": 2970.0
            },
            "net": "LED_NODE",
            "electrical_type": null,
            "side": null
          }
        ]
      },
      {
        "id": "D1",
        "symbol_class": "DIODE",
        "value": "LED_RED",
        "unit": 1,
        "sub_unit": null,
        "package": null,
        "description": null,
        "position": {
          "x": 5000.0,
          "y": 2970.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "ANODE",
            "pos": {
              "x": 4900.0,
              "y": 2970.0
            },
            "net": "LED_NODE",
            "electrical_type": null,
            "side": null
          },
          {
            "number": "2",
            "function": "CATHODE",
            "pos": {
              "x": 5100.0,
              "y": 2970.0
            },
            "net": "GND",
            "electrical_type": null,
            "side": null
          }
        ]
      },
      {
        "id": "VCC1",
        "symbol_class": "VCC",
        "value": "",
        "unit": 1,
        "sub_unit": null,
        "package": null,
        "description": null,
        "position": {
          "x": 4350.0,
          "y": 3600.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "PWR",
            "pos": {
              "x": 4350.0,
              "y": 3500.0
            },
            "net": "VCC",
            "electrical_type": null,
            "side": null
          }
        ]
      },
      {
        "id": "GND1",
        "symbol_class": "GROUND",
        "value": "",
        "unit": 1,
        "sub_unit": null,
        "package": null,
        "description": null,
        "position": {
          "x": 4050.0,
          "y": 2300.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "PWR",
            "pos": {
              "x": 4050.0,
              "y": 2400.0
            },
            "net": "GND",
            "electrical_type": null,
            "side": null
          }
        ]
      }
    ],
    "nets": [
      {
        "name": "VCC",
        "auto_named": false,
        "pins": [
          [
            "VCC1",
            "1"
          ],
          [
            "U1",
            "4"
          ],
          [
            "U1",
            "8"
          ],
          [
            "R1",
            "1"
          ]
        ],
        "labels": [
          {
            "text": "VCC",
            "pos": {
              "x": 4350.0,
              "y": 3600.0
            }
          }
        ]
      },
      {
        "name": "GND",
        "auto_named": false,
        "pins": [
          [
            "GND1",
            "1"
          ],
          [
            "U1",
            "1"
          ],
          [
            "C1",
            "2"
          ],
          [
            "C2",
            "2"
          ],
          [
            "D1",
            "2"
          ]
        ],
        "labels": [
          {
            "text": "GND",
            "pos": {
              "x": 4050.0,
              "y": 2300.0
            }
          }
        ]
      },
      {
        "name": "DISCH_NODE",
        "auto_named": true,
        "pins": [
          [
            "R1",
            "2"
          ],
          [
            "R2",
            "1"
          ],
          [
            "U1",
            "7"
          ]
        ],
        "labels": []
      },
      {
        "name": "TRIG_NODE",
        "auto_named": true,
        "pins": [
          [
            "R2",
            "2"
          ],
          [
            "C1",
            "1"
          ],
          [
            "U1",
            "2"
          ],
          [
            "U1",
            "6"
          ]
        ],
        "labels": []
      },
      {
        "name": "CTRL_NODE",
        "auto_named": true,
        "pins": [
          [
            "U1",
            "5"
          ],
          [
            "C2",
            "1"
          ]
        ],
        "labels": []
      },
      {
        "name": "OUT_NODE",
        "auto_named": false,
        "pins": [
          [
            "U1",
            "3"
          ],
          [
            "R3",
            "1"
          ]
        ],
        "labels": [
          {
            "text": "CLK_OUT",
            "pos": {
              "x": 4500.0,
              "y": 3050.0
            }
          }
        ]
      },
      {
        "name": "LED_NODE",
        "auto_named": true,
        "pins": [
          [
            "R3",
            "2"
          ],
          [
            "D1",
            "1"
          ]
        ],
        "labels": []
      }
    ],
    "warnings": [],
    "metadata": {
      "source": "synthetic",
      "mode": "vector",
      "confidence": 1.0,
      "ocr_confidence": 1.0
    }
  },
  "voltage_divider": {
    "schema_version": "1.0",
    "design": {
      "name": "voltage_divider",
      "page": 1,
      "units": "mils",
      "grid": 100
    },
    "components": [
      {
        "id": "R1",
        "symbol_class": "RESISTOR",
        "value": "10k",
        "unit": 1,
        "position": {
          "x": 4000.0,
          "y": 3000.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "A",
            "pos": {
              "x": 3900.0,
              "y": 3000.0
            },
            "net": "VCC"
          },
          {
            "number": "2",
            "function": "B",
            "pos": {
              "x": 4100.0,
              "y": 3000.0
            },
            "net": "MID"
          }
        ]
      },
      {
        "id": "R2",
        "symbol_class": "RESISTOR",
        "value": "10k",
        "unit": 1,
        "position": {
          "x": 4600.0,
          "y": 3000.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "A",
            "pos": {
              "x": 4500.0,
              "y": 3000.0
            },
            "net": "MID"
          },
          {
            "number": "2",
            "function": "B",
            "pos": {
              "x": 4700.0,
              "y": 3000.0
            },
            "net": "GND"
          }
        ]
      },
      {
        "id": "VCC1",
        "symbol_class": "VCC",
        "value": "",
        "unit": 1,
        "position": {
          "x": 3800.0,
          "y": 3200.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "PWR",
            "pos": {
              "x": 3800.0,
              "y": 3100.0
            },
            "net": "VCC"
          }
        ]
      },
      {
        "id": "GND1",
        "symbol_class": "GROUND",
        "value": "",
        "unit": 1,
        "position": {
          "x": 4800.0,
          "y": 2800.0
        },
        "rotation": 0,
        "mirror": false,
        "src_bbox_px": [],
        "confidence": 1.0,
        "pins": [
          {
            "number": "1",
            "function": "PWR",
            "pos": {
              "x": 4800.0,
              "y": 2900.0
            },
            "net": "GND"
          }
        ]
      }
    ],
    "nets": [
      {
        "name": "VCC",
        "auto_named": false,
        "pins": [
          [
            "R1",
            "1"
          ],
          [
            "VCC1",
            "1"
          ]
        ],
        "labels": [
          {
            "text": "VCC",
            "pos": {
              "x": 3800.0,
              "y": 3200.0
            }
          }
        ]
      },
      {
        "name": "MID",
        "auto_named": true,
        "pins": [
          [
            "R1",
            "2"
          ],
          [
            "R2",
            "1"
          ]
        ],
        "labels": []
      },
      {
        "name": "GND",
        "auto_named": false,
        "pins": [
          [
            "R2",
            "2"
          ],
          [
            "GND1",
            "1"
          ]
        ],
        "labels": [
          {
            "text": "GND",
            "pos": {
              "x": 4800.0,
              "y": 2800.0
            }
          }
        ]
      }
    ],
    "warnings": [],
    "metadata": {
      "source": "synthetic",
      "mode": "vector",
      "confidence": 1.0,
      "ocr_confidence": 1.0
    }
  }
};
