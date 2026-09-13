package com.fakenews.server.domain.auth;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public final class AuthDtos {
    private AuthDtos() {}

    public record SignUpRequest(
            @NotBlank @Email String email,
            @NotBlank @Size(min = 8, max = 72) String password,
            @NotBlank @Size(max = 30) String name
    ) {}

    public record LoginRequest(
            @NotBlank @Email String email,
            @NotBlank String password
    ) {}

    public record TokenResponse(String accessToken, String tokenType, long expiresIn) {}
    public record UserResponse(Long id, String email, String name) {
        static UserResponse from(User user) {
            return new UserResponse(user.getId(), user.getEmail(), user.getName());
        }
    }
}
