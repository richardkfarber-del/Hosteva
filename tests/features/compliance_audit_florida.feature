Feature: Address Eligibility Municipal Compliance Auditing
  As the legal auditing system
  I need to evaluate property data against Pasco and Hillsborough county municipal codes
  So that properties are only approved if they strictly meet local technical compliance constraints

  # Pasco County
  Scenario: Pasco County Property requires Short-Term Rental Business Tax Receipt
    Given a property is located in "Pasco" county
    When the property data is evaluated by the compliance engine
    And the property is missing a Short-Term Rental Business Tax Receipt (Code Chapter 134)
    Then the system must flag the property as non-compliant
    And issue an error referencing "Pasco County Code Chapter 134"

  Scenario: Pasco County Property enforces strict occupancy limits
    Given a property is located in "Pasco" county
    When the property data is evaluated by the compliance engine
    And the property reports guests exceeding the max limit of 10 (Code 134-3)
    Then the system must flag the property as non-compliant
    And issue an error referencing "Pasco County Code 134-3"

  Scenario: Pasco County Property enforces parking requirements
    Given a property is located in "Pasco" county
    When the property data is evaluated by the compliance engine
    And the property provides fewer parking spaces than 1 per bedroom (Code 134-4)
    Then the system must flag the property as non-compliant
    And issue an error referencing "Pasco County Code 134-4"

  # Hillsborough County
  Scenario: Hillsborough County Property requires Vacation Rental License and State Registration
    Given a property is located in "Hillsborough" county
    When the property data is evaluated by the compliance engine
    And the property lacks a Vacation Rental License (Code Chapter 30) or State DBPR registration (FS 509.242)
    Then the system must flag the property as non-compliant
    And issue an error referencing the missing required license

  Scenario: Hillsborough County Property enforces strict occupancy and parking limits
    Given a property is located in "Hillsborough" county
    When the property data is evaluated by the compliance engine
    And the property reports guests exceeding the max limit of 12 (Code 30-5)
    Or the property provides fewer parking spaces than 2 per bedroom (Code 30-6)
    Then the system must flag the property as non-compliant

  Scenario: Hillsborough County Property enforces annual safety inspections
    Given a property is located in "Hillsborough" county
    When the property data is evaluated by the compliance engine
    And the last recorded safety inspection is older than 365 days (Code 30-8)
    Then the system must flag the property as non-compliant
    And issue an error referencing "Hillsborough County Code 30-8"