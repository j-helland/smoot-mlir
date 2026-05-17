#[derive(Clone, PartialEq, Debug)]
pub(crate) struct Unit {
    pub expression: String,
}

impl Unit {
    pub fn parse(expression: &str) -> Self {
        let expression = expression.to_string();
        Self { expression }
    }

    pub fn format(&self) -> String {
        self.expression.clone()
    }
}
