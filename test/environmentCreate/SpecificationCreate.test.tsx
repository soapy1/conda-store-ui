import React from "react";
import { Provider } from "react-redux";
import { fireEvent, render, RenderResult } from "@testing-library/react";
import { SpecificationCreate } from "../../src/features/environmentCreate";
import { mockTheme } from "../testutils";
import { store } from "../../src/store";

describe("<SpecificationCreate />", () => {
  let component: RenderResult;
  const mockOnCreateEnvironment = jest.fn();
  beforeEach(() => {
    component = render(
      mockTheme(
        <Provider store={store}>
          <SpecificationCreate onCreateEnvironment={mockOnCreateEnvironment} />
        </Provider>
      )
    );
  });

  it("should render component", () => {
    expect(component.container).toHaveTextContent("Specification");
  });

  it("should switch the view to the yaml editor", () => {
    const switchButton = component.getByLabelText("Switch to YAML Editor");
    fireEvent.click(switchButton);

    const vatSelectInput = component.container.querySelector(
      ".cm-editor"
    ) as HTMLInputElement;
    expect(vatSelectInput).toBeInTheDocument();
  });

  it("should call handleSubmit in order to create a new env", () => {
    const createButton = component.getByText("Create");
    fireEvent.click(createButton);

    expect(mockOnCreateEnvironment).toHaveBeenCalled();

    const switchButton = component.getByLabelText("Switch to YAML Editor");
    fireEvent.click(switchButton);

    fireEvent.click(createButton);

    expect(mockOnCreateEnvironment).toHaveBeenCalledWith({
      channels: [],
      dependencies: []
    });
  });
});
